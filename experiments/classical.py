#!/usr/bin/env python3
"""
Post-level binary classification with TF-IDF classifiers.

For each condition, trains NB / LR / SVM / XGBoost on TF-IDF features.
Each post inherits its author's label; train/test users come from the
shared split manifest built by experiments/data_prep.ipynb, so results
are directly comparable to finetune.py (same users, same split, same
condition definitions).

Data:
  data/posts/v1/reddit-preprocessed.csv   → post text, keyed by user_id
  data/splits/condition_user_splits.csv   → (condition, user_id, y, split)

Usage:
  python experiments/classical.py [--output results/classical.csv]
"""

import argparse
import warnings
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

PREPROCESSED    = "../data/posts/v1/reddit-preprocessed.csv"
SPLIT_MANIFEST  = "../data/splits/condition_user_splits.csv"
RANDOM_SEED     = 42
MAX_TFIDF_FEAT  = 10_000


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


# ---------------------------------------------------------------------------
# Per-condition dataset builder
# ---------------------------------------------------------------------------

def build_condition_dataset(pre, manifest, condition):
    cond_manifest = manifest[manifest["condition"] == condition]
    if cond_manifest.empty:
        return None, None, None, None

    # expand each (user, split, y) row to that user's posts
    df = cond_manifest.merge(pre, on="user_id", how="inner")

    train = df[df["split"] == "train"]
    test  = df[df["split"] == "test"]

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
    parser.add_argument("--conditions", nargs="+", default=None,
                        help="Subset of conditions to run (default: all in the manifest)")
    args = parser.parse_args()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    pre, manifest = load_data()
    conditions = args.conditions or sorted(manifest["condition"].unique())
    records = []

    for condition in conditions:
        X_train, y_train, X_test, y_test = build_condition_dataset(pre, manifest, condition)
        if X_train is None:
            print(f"  SKIP {condition} (not in split manifest)")
            continue

        n_pos_users = manifest[(manifest["condition"] == condition) & (manifest["y"] == 1)]["user_id"].nunique()
        print(f"\n{condition}: {n_pos_users} pos users, "
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
