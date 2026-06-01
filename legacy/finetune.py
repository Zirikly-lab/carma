import pandas as pd
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset
from transformers import AutoTokenizer, AutoModel, Trainer, TrainingArguments
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
import os
import re

BASE_DIR = 'reddit-splits'
MODEL_NAME = "Qwen/Qwen3-235B-A22B-Instruct-2507"
MAX_LEN = 128
BATCH_SIZE = 1
GRAD_ACCUM = 32
EPOCHS = 3
LR = 2e-5

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1": f1_score(labels, preds, average="weighted"),
        "recall": recall_score(labels, preds, average="weighted"),
        "precision": precision_score(labels, preds, average="weighted"),
    }

def preprocess_arabic(text):
    if not isinstance(text, str):
        text = str(text)
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#(\w+)", r"\1", text)
    text = re.sub(r"[^\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\s\u0021-\u007E]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def get_conditions(base_dir):
    base_dir = os.path.join(base_dir,"")
    
    conditions = []
    for d in os.listdir(base_dir):
        path = os.path.join(base_dir, d)
        if os.path.isdir(path) and os.path.exists(os.path.join(path, "train.csv")) and os.path.exists(os.path.join(path, "test.csv")):
            conditions.append(d)
    return sorted(conditions)

class QwenSequenceClassifier(nn.Module):
    def __init__(self, model_name, num_labels, id2label=None, label2id=None, cache_dir=None):
        super().__init__()
        self.num_labels = num_labels
        self.id2label = id2label if id2label is not None else {i: str(i) for i in range(num_labels)}
        self.label2id = label2id if label2id is not None else {str(i): i for i in range(num_labels)}

        self.backbone = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir=cache_dir
        )

        hidden_size = self.backbone.config.hidden_size
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(hidden_size, num_labels)

        self.config = self.backbone.config
        self.config.num_labels = num_labels
        self.config.id2label = self.id2label
        self.config.label2id = self.label2id

    def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
        outputs = self.backbone(
            input_ids=input_ids,
            attention_mask=attention_mask,
            **kwargs
        )

        last_hidden_state = outputs.last_hidden_state

        if attention_mask is not None:
            lengths = attention_mask.sum(dim=1) - 1
            pooled = last_hidden_state[
                torch.arange(last_hidden_state.size(0), device=last_hidden_state.device),
                lengths
            ]
        else:
            pooled = last_hidden_state[:, -1, :]

        logits = self.classifier(self.dropout(pooled))

        loss = None
        if labels is not None:
            loss = nn.CrossEntropyLoss()(logits, labels)

        return {"loss": loss, "logits": logits}

def train_condition(condition, tokenizer):
    train_df = pd.read_csv(os.path.join(BASE_DIR, f"{condition}/train.csv"))
    test_df = pd.read_csv(os.path.join(BASE_DIR, f"{condition}/test.csv"))

    labels = sorted(train_df["class"].unique().tolist())
    label2id = {l: i for i, l in enumerate(labels)}
    id2label = {i: l for l, i in label2id.items()}

    class TextDataset(Dataset):
        def __init__(self, df):
            self.texts = [preprocess_arabic(t) for t in df["text"].tolist()]
            self.labels = [label2id[l] for l in df["class"].tolist()]

        def __len__(self):
            return len(self.texts)

        def __getitem__(self, idx):
            enc = tokenizer(
                self.texts[idx],
                truncation=True,
                padding="max_length",
                max_length=MAX_LEN,
                return_tensors="pt",
                add_special_tokens=True,
                return_attention_mask=True,
            )
            return {
                "input_ids": enc["input_ids"].squeeze(0),
                "attention_mask": enc["attention_mask"].squeeze(0),
                "labels": torch.tensor(self.labels[idx], dtype=torch.long)
            }

    train_dataset = TextDataset(train_df)
    test_dataset = TextDataset(test_df)

    model = QwenSequenceClassifier(
        MODEL_NAME,
        num_labels=len(labels),
        id2label=id2label,
        label2id=label2id,
        cache_dir="../hf_cache"
    )

    training_args = TrainingArguments(
        output_dir=os.path.join(BASE_DIR, f"Models/{condition}/{MODEL_NAME.replace('/', '_')}"),
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LR,
        fp16=torch.cuda.is_available(),
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_steps=100,
        report_to="none",
        save_safetensors=False,
        remove_unused_columns=False
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
    )

    torch.cuda.empty_cache()

    trainer.train()
    results = trainer.evaluate()

    final_dir = os.path.join(BASE_DIR, f"Models/{condition}/{MODEL_NAME.replace('/', '_')}/final")
    os.makedirs(final_dir, exist_ok=True)

    model.backbone.save_pretrained(final_dir, safe_serialization=False)
    tokenizer.save_pretrained(final_dir)

    torch.save(model.classifier.state_dict(), os.path.join(final_dir, "classifier_head.pt"))

    del model
    del trainer
    torch.cuda.empty_cache()

    return {
        "condition": condition,
        "train_size": len(train_df),
        "test_size": len(test_df),
        "f1": results["eval_f1"],
        "accuracy": results["eval_accuracy"],
        "precision": results["eval_precision"],
        "recall": results["eval_recall"],
    }

if __name__ == "__main__":
    conditions = get_conditions(BASE_DIR)
    print(f"Found {len(conditions)} conditions: {conditions}\n")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        cache_dir="../hf_cache"
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    all_results = []

    for cond in conditions:
        print(f"\n{'='*60}")
        print(f"Training: {cond}")
        print(f"{'='*60}")
        result = train_condition(cond, tokenizer)
        all_results.append(result)

    print(f"\n{'='*100}")
    print(f"{'RESULTS':^100}")
    print(f"{'='*100}")
    print(f"{'condition':<20} | {'train':>8} | {'test':>8} | {'f1':>8} | {'accuracy':>8} | {'precision':>8} | {'recall':>8}")
    print("-" * 100)
    for r in all_results:
        print(f"{r['condition']:<20} | {r['train_size']:>8} | {r['test_size']:>8} | {r['f1']:>8.4f} | {r['accuracy']:>8.4f} | {r['precision']:>8.4f} | {r['recall']:>8.4f}")
    print(f"{'='*100}")

    results_dir = os.path.join(BASE_DIR, f"Models/{MODEL_NAME.replace('/', '_')}")
    os.makedirs(results_dir, exist_ok=True)
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(os.path.join(results_dir, "results.csv"), index=False)