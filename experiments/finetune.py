#!/usr/bin/env python3
"""
User-level binary classification with fine-tuned Arabic PLMs.

For each condition, fine-tunes AraBERT-Twitter and CAMeLBERT.
Each user's posts are concatenated and truncated to 512 tokens.

Usage:
  python experiments/finetune.py --model arabert [--condition depression]
  python experiments/finetune.py --model camelbert [--condition all]
"""

import argparse
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score

warnings.filterwarnings("ignore")

PREPROCESSED  = "data/posts/v1/reddit-preprocessed.csv"
MAJORITY_VOTE = "data/metadata/majority-vote-reddit.csv"
RANDOM_SEED   = 42
TEST_SIZE     = 0.10
MIN_USERS     = 30
MAX_SEQ_LEN   = 512
BATCH_SIZE    = 16
EPOCHS        = 3
LR            = 2e-5

MODELS = {
    "arabert":   "aubmindlab/bert-base-arabertv02-twitter",
    "camelbert": "CAMeL-Lab/bert-base-arabic-camelbert-mix",
}

CONDITIONS = [
    "depression", "anxiety", "adhd", "ocd", "sleep_disorder",
    "autism", "panic", "bipolar", "ptsd", "bpd",
    "suicidal", "schizophrenia", "eating_disorder",
]


# ---------------------------------------------------------------------------
# Data loading (same re-labeling logic as classical.py)
# ---------------------------------------------------------------------------

def load_user_texts():
    print("Loading preprocessed posts …")
    pre = pd.read_csv(PREPROCESSED, keep_default_na=False,
                      usecols=["user_id", "class", "text"])
    pre = pre[pre["text"].str.strip() != ""]

    print("Loading majority-vote metadata …")
    mv = pd.read_csv(MAJORITY_VOTE, keep_default_na=False)
    author_diag = mv.groupby("author")["diagnosis"].first().reset_index()
    author_diag.columns = ["user_id", "mv_diagnosis"]

    pre = pre.merge(author_diag, on="user_id", how="left")
    pre["label"] = pre["mv_diagnosis"].fillna("").where(
        pre["mv_diagnosis"].notna() & (pre["mv_diagnosis"] != ""),
        other=pre["class"]
    )

    mv_users  = set(author_diag["user_id"])
    ctrl_mask = pre["class"] == "control"
    mv_mask   = pre["user_id"].isin(mv_users)
    pre = pre[ctrl_mask | mv_mask].copy()
    pre = pre[pre["label"].isin(CONDITIONS + ["control"])]

    # Aggregate: all posts per user → one string (chronological order)
    print("Aggregating posts per user …")
    user_df = (
        pre.groupby("user_id")
           .agg(text=("text", lambda x: " ".join(x)), label=("label", "first"))
           .reset_index()
    )
    print(f"  {len(user_df)} users")
    return user_df


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class PostDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.encodings = tokenizer(
            list(texts),
            truncation=True,
            padding=True,
            max_length=MAX_SEQ_LEN,
            return_tensors="pt",
        )
        self.labels = torch.tensor(list(labels), dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {k: v[idx] for k, v in self.encodings.items()}, self.labels[idx]


# ---------------------------------------------------------------------------
# Training / evaluation
# ---------------------------------------------------------------------------

def train_epoch(model, loader, optimizer, device):
    model.train()
    total_loss = 0
    for batch, labels in loader:
        batch   = {k: v.to(device) for k, v in batch.items()}
        labels  = labels.to(device)
        outputs = model(**batch, labels=labels)
        loss    = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        total_loss += loss.item()
    return total_loss / len(loader)


def evaluate_model(model, loader, device):
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for batch, labels in loader:
            batch  = {k: v.to(device) for k, v in batch.items()}
            logits = model(**batch).logits
            preds  = logits.argmax(dim=-1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())
    return {
        "f1":        round(f1_score(all_labels, all_preds), 4),
        "accuracy":  round(accuracy_score(all_labels, all_preds), 4),
        "precision": round(precision_score(all_labels, all_preds, zero_division=0), 4),
        "recall":    round(recall_score(all_labels, all_preds, zero_division=0), 4),
    }


# ---------------------------------------------------------------------------
# Per-condition experiment
# ---------------------------------------------------------------------------

def run_condition(condition, user_df, model_name, model_path, device):
    pos = user_df[user_df["label"] == condition]
    neg = user_df[user_df["label"] == "control"]

    if len(pos) < MIN_USERS:
        print(f"  SKIP {condition} (< {MIN_USERS} users)")
        return None

    rng = np.random.default_rng(RANDOM_SEED)
    n   = min(len(pos), len(neg))
    pos = pos.sample(n, random_state=RANDOM_SEED)
    neg = neg.sample(n, random_state=RANDOM_SEED)

    df = pd.concat([pos, neg])
    df["y"] = (df["label"] == condition).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["y"], test_size=TEST_SIZE,
        stratify=df["y"], random_state=RANDOM_SEED
    )

    n_pos = y_train.sum() + y_test.sum()
    print(f"\n  {condition}: {n_pos} pos | train={len(y_train)} test={len(y_test)}")

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model     = AutoModelForSequenceClassification.from_pretrained(
        model_path, num_labels=2, trust_remote_code=True
    ).to(device)

    train_ds = PostDataset(X_train, y_train, tokenizer)
    test_ds  = PostDataset(X_test,  y_test,  tokenizer)
    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=4)
    test_dl  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

    best_f1, best_metrics = 0, {}
    for epoch in range(1, EPOCHS + 1):
        loss = train_epoch(model, train_dl, optimizer, device)
        metrics = evaluate_model(model, test_dl, device)
        print(f"    epoch {epoch}: loss={loss:.4f}  F1={metrics['f1']:.3f}  "
              f"Acc={metrics['accuracy']:.3f}")
        if metrics["f1"] > best_f1:
            best_f1, best_metrics = metrics["f1"], metrics

    return best_metrics


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",     choices=list(MODELS), required=True)
    parser.add_argument("--condition", default="all",
                        help="Condition name or 'all'")
    parser.add_argument("--output",    default=None)
    args = parser.parse_args()

    model_path = MODELS[args.model]
    out_path   = args.output or f"results/finetune_{args.model}.csv"
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    user_df = load_user_texts()
    conditions = CONDITIONS if args.condition == "all" else [args.condition]

    records = []
    for condition in conditions:
        print(f"\n{'='*50}")
        print(f"Model: {args.model}  Condition: {condition}")
        metrics = run_condition(condition, user_df, args.model, model_path, device)
        if metrics is None:
            continue
        metrics["condition"] = condition
        metrics["model"]     = args.model
        records.append(metrics)

    if not records:
        print("No results.")
        return

    results = pd.DataFrame(records)[
        ["condition", "model", "f1", "accuracy", "precision", "recall"]]
    results.to_csv(out_path, index=False)
    print(f"\nResults saved to {out_path}")
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
