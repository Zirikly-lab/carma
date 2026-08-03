#!/usr/bin/env python3
"""
Post-level or user-level binary classification with TF-IDF classifiers.

For each condition, trains NB / LR / SVM / XGBoost on TF-IDF features.
By default each post is its own example (post-level); with --user-level,
each user's posts are concatenated into a single example instead, so
results are directly comparable to finetune.py (same users, same split,
same condition definitions). In both modes, control and diagnosed users
are downsampled to equal counts within each split before building the
dataset, so class balance is defined at the user level regardless of
how many posts each user contributed.

Data:
  data/posts/v1/reddit-preprocessed.csv   → post text, keyed by user_id
  data/splits/condition_user_splits.csv   → (condition, user_id, y, split)

Usage:
  python experiments/classical.py [--output results/classical.csv] [--user-level]
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


def aggregate_user_text(pre):
    """Concatenate each user's posts into a single row of text."""
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
# Per-condition dataset builder
# ---------------------------------------------------------------------------

def build_condition_dataset(text_source, manifest, condition, seed):
    cond_manifest = manifest[manifest["condition"] == condition]
    if cond_manifest.empty:
        return None, None, None, None

    train_users = balance_users(cond_manifest[cond_manifest["split"] == "train"], seed)
    test_users  = balance_users(cond_manifest[cond_manifest["split"] == "test"], seed)

    # expand each (user, y) row to that user's text (post-level or user-level)
    train = train_users.merge(text_source, on="user_id", how="inner")
    test  = test_users.merge(text_source, on="user_id", how="inner")

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
    parser.add_argument("--output", default=None,
                        help="Default: results/classical_<post|user>.csv, based on --user-level")
    parser.add_argument("--conditions", nargs="+", default=None,
                        help="Subset of conditions to run (default: all in the manifest)")
    parser.add_argument("--user-level", action="store_true",
                        help="Concatenate each user's posts into a single example "
                             "(default: post-level, one example per post)")
    args = parser.parse_args()

    level = "user" if args.user_level else "post"
    output = args.output or f"results/classical_{level}.csv"
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    pre, manifest = load_data()
    text_source = aggregate_user_text(pre) if args.user_level else pre[["user_id", "text"]]
    conditions = args.conditions or sorted(manifest["condition"].unique())
    records = []

    for condition in conditions:
        X_train, y_train, X_test, y_test = build_condition_dataset(
            text_source, manifest, condition, RANDOM_SEED)
        if X_train is None:
            print(f"  SKIP {condition} (not in split manifest)")
            continue

        print(f"\n{condition} ({level}-level): "
              f"train={len(y_train)} ({y_train.sum()} pos), "
              f"test={len(y_test)} ({y_test.sum()} pos)")

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
            row["level"] = level
            records.append(row)
            print(f"  {model_name}: F1={row['f1']:.3f}  "
                  f"Acc={row['accuracy']:.3f}  "
                  f"P={row['precision']:.3f}  R={row['recall']:.3f}")

    results = pd.DataFrame(records)[
        ["condition", "level", "model", "f1", "accuracy", "precision", "recall"]]
    results.to_csv(output, index=False)
    print(f"\nResults saved to {output}")

    # Summary: best F1 per condition
    print("\nBest F1 per condition:")
    best = results.loc[results.groupby("condition")["f1"].idxmax()]
    print(best[["condition", "model", "f1"]].to_string(index=False))


if __name__ == "__main__":
    main()
