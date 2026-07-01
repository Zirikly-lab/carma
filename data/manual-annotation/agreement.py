#!/usr/bin/env python3
"""
Inter-annotator agreement between Fady, Nour, and Qwen (LLM).

Outputs:
  - Pairwise % agreement and Cohen's kappa
  - Per-label precision / recall / F1 for each pair
  - Confusion matrices
  - All-three agreement breakdown
"""

import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

FADY_PATH = "data/manual-annotation/reddit-sample-fady.csv"
NOUR_PATH  = "data/manual-annotation/reddit-sample-nour.csv"
QWEN_PATH  = "data/manual-annotation/reddit-sample-qwen.csv"

LABELS = ["TP", "FP", "NA"]
VALID  = set(LABELS)


def load_data():
    fady = pd.read_csv(FADY_PATH, keep_default_na=False)
    nour = pd.read_csv(NOUR_PATH,  keep_default_na=False)
    qwen = pd.read_csv(QWEN_PATH,  keep_default_na=False)

    df = fady[["id", "diagnosis", "Label"]].rename(columns={"Label": "fady"})
    df = df.merge(nour[["id", "nour_label"]].rename(columns={"nour_label": "nour"}), on="id")
    df = df.merge(qwen[["id", "annotation"]].rename(columns={"annotation": "qwen"}), on="id")
    return df


def pairwise_kappa(a, b):
    k   = cohen_kappa_score(a, b, labels=LABELS)
    pct = (a == b).mean() * 100
    return k, pct


def per_label_stats(a, b, name_a, name_b):
    rows = []
    for lbl in LABELS:
        both  = ((a == lbl) & (b == lbl)).sum()
        a_n   = (a == lbl).sum()
        b_n   = (b == lbl).sum()
        prec  = both / b_n * 100 if b_n else float("nan")
        rec   = both / a_n * 100 if a_n else float("nan")
        f1    = 2 * prec * rec / (prec + rec) if (prec + rec) else float("nan")
        rows.append({
            "label":              lbl,
            f"{name_a}_count":    a_n,
            f"{name_b}_count":    b_n,
            "agree":              both,
            f"prec({name_b}→{name_a})": prec,
            f"rec({name_a}→{name_b})":  rec,
            "F1":                 f1,
        })
    return pd.DataFrame(rows)


def confusion(a, b, name_a, name_b):
    cm = confusion_matrix(a, b, labels=LABELS)
    return pd.DataFrame(
        cm,
        index=  [f"{name_a}={l}" for l in LABELS],
        columns=[f"{name_b}={l}" for l in LABELS],
    )


def main():
    df = load_data()
    print(f"Total rows: {len(df)}")

    mask = {
        "fady": df["fady"].isin(VALID),
        "nour": df["nour"].isin(VALID),
        "qwen": df["qwen"].isin(VALID),
    }
    for name, m in mask.items():
        inv = df.loc[~m, name].value_counts().to_dict()
        print(f"  {name}: {m.sum()} valid, {(~m).sum()} invalid {inv}")

    pairs = [
        ("Fady", "Nour", "fady", "nour"),
        ("Fady", "Qwen", "fady", "qwen"),
        ("Nour", "Qwen", "nour", "qwen"),
    ]

    # ------------------------------------------------------------------ #
    print("\n" + "=" * 60)
    print("PAIRWISE AGREEMENT SUMMARY")
    print("=" * 60)
    for a_name, b_name, a_col, b_col in pairs:
        m = mask[a_col] & mask[b_col]
        a, b = df.loc[m, a_col], df.loc[m, b_col]
        k, pct = pairwise_kappa(a, b)
        print(f"\n{a_name} vs {b_name}  (n={len(a)})")
        print(f"  % agree : {pct:.1f}%")
        print(f"  Cohen κ : {k:.3f}")

    # ------------------------------------------------------------------ #
    print("\n" + "=" * 60)
    print("PER-LABEL BREAKDOWN (precision / recall / F1)")
    print("  prec(B→A) = of B's calls for label, how many A agrees")
    print("  rec(A→B)  = of A's calls for label, how many B agrees")
    print("=" * 60)
    for a_name, b_name, a_col, b_col in pairs:
        m = mask[a_col] & mask[b_col]
        a, b = df.loc[m, a_col], df.loc[m, b_col]
        print(f"\n--- {a_name} vs {b_name} ---")
        print(per_label_stats(a, b, a_name, b_name).to_string(index=False))

    # ------------------------------------------------------------------ #
    print("\n" + "=" * 60)
    print("CONFUSION MATRICES")
    print("=" * 60)
    for a_name, b_name, a_col, b_col in pairs:
        m = mask[a_col] & mask[b_col]
        a, b = df.loc[m, a_col], df.loc[m, b_col]
        print(f"\n--- {a_name} (rows) vs {b_name} (cols) ---")
        print(confusion(a, b, a_name, b_name).to_string())

    # ------------------------------------------------------------------ #
    mask_all = mask["fady"] & mask["nour"] & mask["qwen"]
    df3 = df[mask_all]
    all_agree = (df3["fady"] == df3["nour"]) & (df3["nour"] == df3["qwen"])
    print(f"\n{'='*60}")
    print(f"ALL THREE AGREE (n={len(df3)}): {all_agree.sum()} rows = {all_agree.mean()*100:.1f}%")
    print("\nLabel breakdown where all three agree:")
    print(df3.loc[all_agree, "fady"].value_counts())
    print("\nTop disagreement patterns (fady / nour / qwen):")
    print(df3.loc[~all_agree, ["fady", "nour", "qwen"]].value_counts().head(15))


if __name__ == "__main__":
    main()
