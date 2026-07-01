#!/usr/bin/env python3
"""
Post-level binary classification with TF-IDF classifiers.

For each condition, trains NB / LR / SVM / XGBoost on TF-IDF features.
Each post inherits its author's label; split is enforced at user level
so no user's posts appear in both train and test.

Data:
  legacy preprocessed  → post histories (text, user_id, class)
  majority-vote-reddit → correct diagnosis labels per author

Usage:
  python experiments/classical.py [--output results/classical.csv]
"""

import argparse
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

PREPROCESSED   = "data/posts/v1/reddit-preprocessed.csv"
MAJORITY_VOTE  = "data/metadata/majority-vote-reddit.csv"
RANDOM_SEED    = 42
TEST_SIZE      = 0.10
MIN_USERS      = 30        # skip conditions below this threshold
MAX_TFIDF_FEAT = 10_000

CONDITIONS = [
    "depression", "anxiety", "adhd", "ocd", "sleep_disorder",
    "autism", "panic", "bipolar", "ptsd", "bpd",
    "suicidal", "schizophrenia", "eating_disorder",
]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data():
    print("Loading preprocessed posts …")
    pre = pd.read_csv(PREPROCESSED, keep_default_na=False,
                      usecols=["user_id", "class", "text"])
    pre = pre[pre["text"].str.strip() != ""]

    print("Loading majority-vote metadata …")
    mv = pd.read_csv(MAJORITY_VOTE, keep_default_na=False)
    # Take primary diagnosis per author (first occurrence)
    author_diag = mv.groupby("author")["diagnosis"].first().reset_index()
    author_diag.columns = ["user_id", "mv_diagnosis"]

    pre = pre.merge(author_diag, on="user_id", how="left")

    # Re-label: MV authors get their majority-vote diagnosis; others keep class
    pre["label"] = pre["mv_diagnosis"].fillna("").where(
        pre["mv_diagnosis"].notna() & (pre["mv_diagnosis"] != ""),
        other=pre["class"]
    )

    # Keep only control users (class == "control") and MV-diagnosed users
    mv_users  = set(author_diag["user_id"])
    ctrl_mask = pre["class"] == "control"
    mv_mask   = pre["user_id"].isin(mv_users)
    pre = pre[ctrl_mask | mv_mask].copy()

    # Drop rows where label is still empty
    pre = pre[pre["label"].isin(CONDITIONS + ["control"])]

    print(f"  {pre['user_id'].nunique()} users, {len(pre)} posts after cleaning")
    return pre


# ---------------------------------------------------------------------------
# Per-condition dataset builder
# ---------------------------------------------------------------------------

def build_condition_dataset(pre, condition):
    pos_users = pre[pre["label"] == condition]["user_id"].unique()
    neg_users = pre[pre["label"] == "control"]["user_id"].unique()

    if len(pos_users) < MIN_USERS:
        return None, None, None, None

    # Balance: sample equal-size control set
    rng = np.random.default_rng(RANDOM_SEED)
    n = min(len(pos_users), len(neg_users))
    pos_sample = rng.choice(pos_users, n, replace=False)
    neg_sample = rng.choice(neg_users, n, replace=False)

    # User-level train/test split
    pos_train_u, pos_test_u = train_test_split(
        pos_sample, test_size=TEST_SIZE, random_state=RANDOM_SEED)
    neg_train_u, neg_test_u = train_test_split(
        neg_sample, test_size=TEST_SIZE, random_state=RANDOM_SEED)

    train_users = set(pos_train_u) | set(neg_train_u)
    test_users  = set(pos_test_u)  | set(neg_test_u)

    # Expand to posts
    all_users = set(pos_sample) | set(neg_sample)
    df = pre[pre["user_id"].isin(all_users)].copy()
    df["y"] = (df["label"] == condition).astype(int)

    train = df[df["user_id"].isin(train_users)]
    test  = df[df["user_id"].isin(test_users)]

    return train["text"], train["y"], test["text"], test["y"]


# ---------------------------------------------------------------------------
# Classifiers
# ---------------------------------------------------------------------------

MODELS = {
    "NB":   lambda: MultinomialNB(),
    "LR":   lambda: LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs",
                                        n_jobs=-1),
    "SVM":  lambda: LinearSVC(max_iter=2000, C=1.0),
    "XGB":  lambda: XGBClassifier(n_estimators=200, max_depth=5, learning_rate=0.1,
                                   use_label_encoder=False, eval_metric="logloss",
                                   n_jobs=-1, random_state=RANDOM_SEED),
}


def evaluate(model_name, clf, vec, X_test, y_test):
    X_te = vec.transform(X_test)
    y_pred = clf.predict(X_te)
    return {
        "model":     model_name,
        "f1":        round(f1_score(y_test, y_pred), 4),
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred, zero_division=0), 4),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/classical.csv")
    parser.add_argument("--conditions", nargs="+", default=CONDITIONS)
    args = parser.parse_args()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    pre = load_data()
    records = []

    for condition in args.conditions:
        X_train, y_train, X_test, y_test = build_condition_dataset(pre, condition)
        if X_train is None:
            print(f"  SKIP {condition} (< {MIN_USERS} users)")
            continue

        n_pos = (y_train == 1).sum() + (y_test == 1).sum()
        print(f"\n{condition}: {n_pos} pos users, "
              f"train={len(y_train)} posts, test={len(y_test)} posts")

        vec = TfidfVectorizer(
            max_features=MAX_TFIDF_FEAT,
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=2,
        )
        X_tr = vec.fit_transform(X_train)

        for model_name, make_clf in MODELS.items():
            clf = make_clf()
            clf.fit(X_tr, y_train)
            row = evaluate(model_name, clf, vec, X_test, y_test)
            row["condition"] = condition
            records.append(row)
            print(f"  {model_name}: F1={row['f1']:.3f}  "
                  f"Acc={row['accuracy']:.3f}  "
                  f"P={row['precision']:.3f}  R={row['recall']:.3f}")

    results = pd.DataFrame(records)[
        ["condition", "model", "f1", "accuracy", "precision", "recall"]]
    results.to_csv(args.output, index=False)
    print(f"\nResults saved to {args.output}")

    # Summary: best F1 per condition
    print("\nBest F1 per condition:")
    best = results.loc[results.groupby("condition")["f1"].idxmax()]
    print(best[["condition", "model", "f1"]].to_string(index=False))


if __name__ == "__main__":
    main()
