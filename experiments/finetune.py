#!/usr/bin/env python3
"""
Post-level or user-level binary classification with fine-tuned Arabic PLMs.

For each condition, fine-tunes AraBERT-Twitter and CAMeLBERT.
By default each post is its own example (post-level, truncated to 512
tokens); with --user-level, each user's posts are concatenated into a
single example (also truncated to 512 tokens) instead, so results are
directly comparable to classical.py (same users, same split, same
condition definitions). In both modes, control and diagnosed users are
downsampled to equal counts within each split before building the
dataset, so class balance is defined at the user level regardless of
how many posts each user contributed.

Usage:
  python experiments/finetune.py --model arabert [--condition depression] [--user-level]
  python experiments/finetune.py --model camelbert [--condition all]
"""

import argparse
import warnings
from functools import partial
import pandas as pd
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score

warnings.filterwarnings("ignore")

PREPROCESSED   = "../data/posts/v1/reddit-preprocessed.csv"
SPLIT_MANIFEST = "../data/splits/condition_user_splits.csv"
MAX_SEQ_LEN    = 512
BATCH_SIZE     = 16
EPOCHS         = 3
LR             = 2e-5
RANDOM_SEED    = 42

MODELS = {
    "arabert":   "aubmindlab/bert-base-arabertv02-twitter",
    "camelbert": "CAMeL-Lab/bert-base-arabic-camelbert-mix",
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data():
    print("Loading preprocessed posts …")
    pre = pd.read_csv(PREPROCESSED, keep_default_na=False,
                      usecols=["user_id", "text"])
    pre = pre[pre["text"].str.strip() != ""]

    print("Loading split manifest …")
    manifest = pd.read_csv(SPLIT_MANIFEST, keep_default_na=False)

    print(f"  {pre['user_id'].nunique():,} users with posts, "
          f"{manifest['user_id'].nunique():,} users in manifest, "
          f"{manifest['condition'].nunique()} conditions")
    return pre, manifest


def aggregate_user_text(pre):
    """Concatenate each user's posts into a single row of text (chronological order as stored)."""
    return pre.groupby("user_id")["text"].apply(lambda x: " ".join(x)).reset_index()


def balance_users(df, seed):
    """Downsample the majority class so control/diagnosed users are equal in count."""
    counts = df["y"].value_counts()
    if len(counts) < 2:
        return df
    n = counts.min()
    parts = [g.sample(n=n, random_state=seed) for _, g in df.groupby("y")]
    return pd.concat(parts).sample(frac=1, random_state=seed).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class PostDataset(Dataset):
    """Tokenizes lazily per-example; padding happens per-batch in collate_fn.

    Eagerly tokenizing an entire split up front (as before) spikes memory
    proportional to split size, which OOMs on post-level splits (100k+ rows)
    under a constrained cgroup. Tokenizing one example at a time keeps peak
    memory bounded by batch size regardless of split size or device.
    """
    def __init__(self, texts, labels, tokenizer):
        self.texts = list(texts)
        self.labels = list(labels)
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx], truncation=True, max_length=MAX_SEQ_LEN,
        )
        return encoding, self.labels[idx]


def collate_batch(batch, tokenizer):
    encodings, labels = zip(*batch)
    padded = tokenizer.pad(list(encodings), return_tensors="pt")
    return padded, torch.tensor(labels, dtype=torch.long)


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

def run_condition(condition, manifest, text_source, model_path, device, seed, level):
    cond_manifest = manifest[manifest["condition"] == condition]
    if cond_manifest.empty:
        print(f"  SKIP {condition} (not in split manifest)")
        return None

    train_users = balance_users(cond_manifest[cond_manifest["split"] == "train"], seed)
    test_users  = balance_users(cond_manifest[cond_manifest["split"] == "test"], seed)

    train = train_users.merge(text_source, on="user_id", how="inner")
    test  = test_users.merge(text_source, on="user_id", how="inner")

    print(f"\n  {condition} ({level}-level): "
          f"train={len(train)} ({train['y'].sum()} pos), "
          f"test={len(test)} ({test['y'].sum()} pos)")

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model     = AutoModelForSequenceClassification.from_pretrained(
        model_path, num_labels=2, trust_remote_code=True
    ).to(device)

    collate = partial(collate_batch, tokenizer=tokenizer)
    train_ds = PostDataset(train["text"], train["y"], tokenizer)
    test_ds  = PostDataset(test["text"],  test["y"],  tokenizer)
    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=4,
                           collate_fn=collate)
    test_dl  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False, num_workers=4,
                           collate_fn=collate)

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
    parser.add_argument("--output",    default=None,
                        help="Default: results/finetune_<model>_<post|user>.csv, based on --user-level")
    parser.add_argument("--user-level", action="store_true",
                        help="Concatenate each user's posts into a single example "
                             "(default: post-level, one example per post)")
    args = parser.parse_args()

    model_path = MODELS[args.model]
    level      = "user" if args.user_level else "post"
    out_path   = args.output or f"results/finetune_{args.model}_{level}.csv"
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    pre, manifest = load_data()
    text_source = aggregate_user_text(pre) if args.user_level else pre[["user_id", "text"]]
    conditions = sorted(manifest["condition"].unique()) if args.condition == "all" else [args.condition]

    records = []
    for condition in conditions:
        print(f"\n{'='*50}")
        print(f"Model: {args.model}  Condition: {condition}  Level: {level}")
        metrics = run_condition(condition, manifest, text_source, model_path, device,
                                 RANDOM_SEED, level)
        if metrics is None:
            continue
        metrics["condition"] = condition
        metrics["model"]     = args.model
        metrics["level"]     = level
        records.append(metrics)

    if not records:
        print("No results.")
        return

    results = pd.DataFrame(records)[
        ["condition", "level", "model", "f1", "accuracy", "precision", "recall"]]
    results.to_csv(out_path, index=False)
    print(f"\nResults saved to {out_path}")
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
