import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import os

BASE_DIR = 'twitter-splits'
CONDITION = "ptsd"
MODEL_NAME = "bert-base-uncased"
MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 3
LR = 2e-5

train_df = pd.read_csv(os.path.join(BASE_DIR, f"{CONDITION}/train.csv"))
test_df = pd.read_csv(os.path.join(BASE_DIR, f"{CONDITION}/test.csv"))

labels = train_df["class"].unique().tolist()
label2id = {l: i for i, l in enumerate(labels)}
id2label = {i: l for l, i in label2id.items()}

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

class TextDataset(Dataset):
    def __init__(self, df):
        self.texts = df["text"].tolist()
        self.labels = [label2id[l] for l in df["class"].tolist()]

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = tokenizer(self.texts[idx], truncation=True, padding="max_length", max_length=MAX_LEN, return_tensors="pt")
        return {
            "input_ids": enc["input_ids"].squeeze(),
            "attention_mask": enc["attention_mask"].squeeze(),
            "labels": torch.tensor(self.labels[idx])
        }

train_dataset = TextDataset(train_df)
test_dataset = TextDataset(test_df)

model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(labels), id2label=id2label, label2id=label2id)

training_args = TrainingArguments(
    output_dir=os.path.join(BASE_DIR, f"output/{CONDITION}"),
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    learning_rate=LR,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    logging_steps=100,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

trainer.train()
trainer.save_model(os.path.join(BASE_DIR, f"output/{CONDITION}/final"))
