#!/usr/bin/env python3
"""
Inter-annotator agreement between saad, Nour, Qwen (LLM), and Jais (LLM).

Outputs:
  - Pairwise % agreement and Cohen's kappa
  - Per-label precision / recall / F1 for each pair
  - Confusion matrices
  - All-four agreement breakdown
"""

import argparse

import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

saad_PATH = "../saad.csv"
NOUR_PATH  = "../nour.csv"
QWEN_PATH  = "../qwen.csv"
JAIS_PATH  = "../jais.csv"

LABELS = ["TP", "FP"]
VALID  = set(LABELS)


def load_data():
    saad = pd.read_csv(saad_PATH, keep_default_na=False)
    nour = pd.read_csv(NOUR_PATH,  keep_default_na=False)
    qwen = pd.read_csv(QWEN_PATH,  keep_default_na=False)
    jais = pd.read_csv(JAIS_PATH,  keep_default_na=False)

    df = saad[["id", "diagnosis", "saad"]].rename(columns={"saad": "saad"})
    df = df.merge(nour[["id", "nour"]].rename(columns={"nour": "nour"}), on="id")
    df = df.merge(qwen[["id", "annotation"]].rename(columns={"annotation": "qwen"}), on="id")
    df = df.merge(jais[["id", "annotation"]].rename(columns={"annotation": "jais"}), on="id")
    # discard autism entries
    df = df[df["diagnosis"] != "autism"]
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


PAIRS = [
    ("saad", "Nour", "saad", "nour"),
    ("saad", "Qwen", "saad", "qwen"),
    ("saad", "Jais", "saad", "jais"),
    ("Nour", "Qwen", "nour", "qwen"),
    ("Nour", "Jais", "nour", "jais"),
    ("Qwen", "Jais", "qwen", "jais"),
]


def report(df):
    """Print the full agreement report (pairwise kappa, per-label
    breakdown, confusion matrices, all-four agreement) for the given
    dataframe slice."""
    print(f"Total rows: {len(df)}")

    mask = {
        "saad": df["saad"].isin(VALID),
        "nour": df["nour"].isin(VALID),
        "qwen": df["qwen"].isin(VALID),
        "jais": df["jais"].isin(VALID),
    }
    for name, m in mask.items():
        inv = df.loc[~m, name].value_counts().to_dict()
        print(f"  {name}: {m.sum()} valid, {(~m).sum()} invalid {inv}")

    # ------------------------------------------------------------------ #
    print("\n" + "=" * 60)
    print("PAIRWISE AGREEMENT SUMMARY")
    print("=" * 60)
    for a_name, b_name, a_col, b_col in PAIRS:
        m = mask[a_col] & mask[b_col]
        a, b = df.loc[m, a_col], df.loc[m, b_col]
        print(f"\n{a_name} vs {b_name}  (n={len(a)})")
        if len(a) == 0:
            print("  insufficient data")
            continue
        k, pct = pairwise_kappa(a, b)
        print(f"  % agree : {pct:.1f}%")
        print(f"  Cohen κ : {k:.3f}")

    # ------------------------------------------------------------------ #
    print("\n" + "=" * 60)
    print("PER-LABEL BREAKDOWN (precision / recall / F1)")
    print("  prec(B→A) = of B's calls for label, how many A agrees")
    print("  rec(A→B)  = of A's calls for label, how many B agrees")
    print("=" * 60)
    for a_name, b_name, a_col, b_col in PAIRS:
        m = mask[a_col] & mask[b_col]
        a, b = df.loc[m, a_col], df.loc[m, b_col]
        print(f"\n--- {a_name} vs {b_name} ---")
        if len(a) == 0:
            print("  insufficient data")
            continue
        print(per_label_stats(a, b, a_name, b_name).to_string(index=False))

    # ------------------------------------------------------------------ #
    print("\n" + "=" * 60)
    print("CONFUSION MATRICES")
    print("=" * 60)
    for a_name, b_name, a_col, b_col in PAIRS:
        m = mask[a_col] & mask[b_col]
        a, b = df.loc[m, a_col], df.loc[m, b_col]
        print(f"\n--- {a_name} (rows) vs {b_name} (cols) ---")
        if len(a) == 0:
            print("  insufficient data")
            continue
        print(confusion(a, b, a_name, b_name).to_string())

    # ------------------------------------------------------------------ #
    mask_all = mask["saad"] & mask["nour"] & mask["qwen"] & mask["jais"]
    df4 = df[mask_all]
    print(f"\n{'='*60}")
    if len(df4) == 0:
        print("ALL FOUR AGREE: insufficient data")
        return
    all_agree = (
        (df4["saad"] == df4["nour"]) &
        (df4["nour"] == df4["qwen"]) &
        (df4["qwen"] == df4["jais"])
    )
    print(f"ALL FOUR AGREE (n={len(df4)}): {all_agree.sum()} rows = {all_agree.mean()*100:.1f}%")
    print("\nLabel breakdown where all four agree:")
    print(df4.loc[all_agree, "saad"].value_counts())
    print("\nTop disagreement patterns (saad / nour / qwen / jais):")
    print(df4.loc[~all_agree, ["saad", "nour", "qwen", "jais"]].value_counts().head(15))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fine-grained",
        action="store_true",
        help="In addition to the pooled report, also break down agreement "
             "per condition (diagnosis).",
    )
    args = parser.parse_args()

    df = load_data()

    print("#" * 70)
    print("POOLED (ALL CONDITIONS)")
    print("#" * 70)
    report(df)

    if args.fine_grained:
        for condition in sorted(df["diagnosis"].dropna().unique()):
            sub = df[df["diagnosis"] == condition]
            print("\n" + "#" * 70)
            print(f"CONDITION: {condition}  (n={len(sub)})")
            print("#" * 70)
            report(sub)


if __name__ == "__main__":
    main()
