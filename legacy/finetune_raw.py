"""
Arabic Mental Health Classification - RAW DATA VERSION
Uses minimal preprocessing to preserve signal
"""
import pandas as pd
import torch
import numpy as np
from torch.utils.data import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
import os
import re

# ============== CONFIGURATION ==============
# NOTE: If performance dropped, it's because reddit-splits/ contains
# heavily preprocessed data that removes mental health keywords.
# For best results, recreate splits WITHOUT the keyword filtering.
BASE_DIR = 'reddit-splits'  
MODEL_NAME = "aubmindlab/bert-base-arabertv02-twitter"
MAX_LEN = 128
BATCH_SIZE = 8
EPOCHS = 3
LR = 2e-5
# ===========================================

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1": f1_score(labels, preds, average="weighted"),
        "recall": recall_score(labels, preds, average="weighted"),
        "precision": precision_score(labels, preds, average="weighted"),
    }

def preprocess_arabic_minimal(text):
    """
    MINIMAL preprocessing - only remove noise, keep everything else.
    AraBERT handles normalization internally.
    """
    if not isinstance(text, str):
        text = str(text) if text else ""
    
    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)
    # Remove @mentions
    text = re.sub(r"@\w+", " ", text)
    # Remove hashtag symbol but keep the word
    text = re.sub(r"#(\w+)", r"\1", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

def get_conditions(base_dir):
    """Get list of conditions that have train/test splits"""
    conditions = []
    for d in os.listdir(base_dir):
        path = os.path.join(base_dir, d)
        if os.path.isdir(path):
            train_path = os.path.join(path, "train.csv")
            test_path = os.path.join(path, "test.csv")
            if os.path.exists(train_path) and os.path.exists(test_path):
                conditions.append(d)
    return sorted(conditions)

def train_condition(condition, tokenizer, base_dir=BASE_DIR):
    """Train a binary classifier for one condition vs control"""
    print(f"\n{'='*60}")
    print(f"Training: {condition}")
    print(f"{'='*60}")
    
    train_df = pd.read_csv(os.path.join(base_dir, f"{condition}/train.csv"))
    test_df = pd.read_csv(os.path.join(base_dir, f"{condition}/test.csv"))
    
    print(f"Train samples: {len(train_df)}")
    print(f"Test samples: {len(test_df)}")
    
    # Create label mapping
    labels = sorted(train_df["class"].unique().tolist())
    label2id = {l: i for i, l in enumerate(labels)}
    id2label = {i: l for l, i in label2id.items()}
    print(f"Labels: {labels}")
    
    class TextDataset(Dataset):
        def __init__(self, df):
            self.texts = [preprocess_arabic_minimal(t) for t in df["text"].tolist()]
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
            )
            return {
                "input_ids": enc["input_ids"].squeeze(),
                "attention_mask": enc["attention_mask"].squeeze(),
                "labels": torch.tensor(self.labels[idx])
            }

    train_dataset = TextDataset(train_df)
    test_dataset = TextDataset(test_df)
    
    # Initialize model
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(labels),
        label2id=label2id,
        id2label=id2label,
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=f"./results_{condition}",
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        learning_rate=LR,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=50,
        report_to="none",
        fp16=torch.cuda.is_available(),
        dataloader_num_workers=0,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
    )
    
    # Train
    trainer.train()
    
    # Evaluate
    results = trainer.evaluate()
    print(f"\nResults for {condition}:")
    for k, v in results.items():
        print(f"  {k}: {v:.4f}")
    
    return {
        "condition": condition,
        "accuracy": results["eval_accuracy"],
        "f1": results["eval_f1"],
        "recall": results["eval_recall"],
        "precision": results["eval_precision"],
        "train_samples": len(train_df),
        "test_samples": len(test_df),
    }

def main():
    print("="*60)
    print("Arabic Mental Health Classification - RAW DATA")
    print("Model:", MODEL_NAME)
    print("Using MINIMAL preprocessing (no heavy normalization)")
    print("="*60)
    
    # Check for GPU
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("Running on CPU")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    # Get available conditions
    conditions = get_conditions(BASE_DIR)
    print(f"\nFound {len(conditions)} conditions: {conditions}")
    
    if not conditions:
        print("ERROR: No conditions found! Check BASE_DIR path.")
        return
    
    # Train all conditions
    all_results = []
    for condition in conditions:
        try:
            result = train_condition(condition, tokenizer)
            all_results.append(result)
        except Exception as e:
            print(f"ERROR training {condition}: {e}")
            continue
    
    # Summary table
    print("\n" + "="*80)
    print("FINAL RESULTS SUMMARY")
    print("="*80)
    
    df_results = pd.DataFrame(all_results)
    print(df_results.to_string(index=False))
    
    # Save results
    df_results.to_csv("results_raw_data.csv", index=False)
    print("\nResults saved to results_raw_data.csv")
    
    # Averages
    print("\n" + "-"*40)
    print("AVERAGES")
    print("-"*40)
    print(f"Accuracy:  {df_results['accuracy'].mean():.4f}")
    print(f"F1:        {df_results['f1'].mean():.4f}")
    print(f"Recall:    {df_results['recall'].mean():.4f}")
    print(f"Precision: {df_results['precision'].mean():.4f}")

if __name__ == "__main__":
    main()
