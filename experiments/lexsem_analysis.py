#!/usr/bin/env python3
"""
Lexical differences between diagnosed and control users on CARMA (Reddit).

Two analyses, both at the pooled corpus level (all diagnosed users vs. all
control users, as defined by data/splits/condition_user_splits.csv):

  1. Log-odds-ratio with an informative Dirichlet prior (Monroe, Colaresi &
     Quinn, 2008) over unigrams, using the combined diagnosed+control corpus
     as the background prior. Surfaces the words most distinctively
     over-used by each group, correcting for raw frequency differences.

  2. Four summary statistics per group: type-token ratio (vocabulary
     richness, computed on an equal-size token subsample so it's comparable
     across groups of very different total size), mean tokens per post,
     first-person rate, and negation rate. The latter two are tagged with a
     CAMeL Tools morphological cascade (MSA MLE disambiguator -> Egyptian MLE
     disambiguator -> Gulf morphology-db, each in turn) rather than a fixed
     word list, since Arabic is pro-drop -- first person is usually carried
     by verb/clitic morphology (e.g. per=1 agreement, a 1s/1p enclitic), not
     a free-standing pronoun -- and negation is often a proclitic circumfix
     (Egyptian ma-...-sh) rather than its own token. A small fallback list
     covers the few free-standing dialectal negators absent from all three
     databases (verified empirically; see FALLBACK_NEGATION_TOKENS). This
     requires `pip install camel-tools` plus the data packages listed below.

Data:
  data/posts/v1/reddit-preprocessed.csv   -> post text, keyed by user_id
  data/splits/condition_user_splits.csv   -> (condition, user_id, y, split)

Setup (one-time, for the morphological tagger):
  pip install camel-tools
  camel_data -i morphology-db-msa-r13 disambig-mle-calima-msa-r13 \
                disambig-mle-calima-egy-r13 morphology-db-glf-01

Usage:
  python experiments/lexsem_analysis.py [--output results/lexsem.csv] [--top-k 15]
"""

import argparse
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

try:
    from camel_tools.disambig.mle import MLEDisambiguator
    from camel_tools.morphology.analyzer import Analyzer as CamelAnalyzer
    from camel_tools.morphology.database import MorphologyDB
except ImportError as e:
    raise ImportError(
        "camel-tools is required for morphological first-person/negation "
        "tagging. Install with `pip install camel-tools`, then download the "
        "required data with `camel_data -i morphology-db-msa-r13 "
        "disambig-mle-calima-msa-r13 disambig-mle-calima-egy-r13 "
        "morphology-db-glf-01`."
    ) from e

SCRIPT_DIR      = Path(__file__).resolve().parent
PREPROCESSED    = SCRIPT_DIR / "../data/posts/v1/reddit-preprocessed.csv"
SPLIT_MANIFEST  = SCRIPT_DIR / "../data/splits/condition_user_splits.csv"
STOPWORDS_PATH  = SCRIPT_DIR / "ar_stopwords.txt"
RANDOM_SEED     = 42
MIN_TOKEN_FREQ  = 10     # drop rarer tokens from the log-odds ranking (noisy z-scores)
MIN_USER_FREQ   = 5      # drop tokens whose count in a group comes from too few distinct
                          # users there (guards against one prolific/repetitive poster
                          # masquerading as a group-level "keyword")
DIRICHLET_ALPHA0_SCALE = 1.0  # background prior weight multiplier

# Free-standing dialectal negators with no lexical entry in the MSA, Egyptian,
# or Gulf CAMeL Tools databases (verified empirically -- each returns zero or
# backoff-only analyses), so the morphological cascade below can't see them.
# This is the sole remaining hand-curated piece; everything else free-person/
# negation-related that morphology can resolve is handled in tag_post().
FALLBACK_NEGATION_TOKENS = {"ماكو", "مافيه"}

ARABIC_DIACRITICS = re.compile(r"[ً-ْٰـ]")  # harakat + tatweel
TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)


# ---------------------------------------------------------------------------
# Text normalization / tokenization
# ---------------------------------------------------------------------------

def normalize_arabic(text):
    """Light orthographic normalization, matching the variant classes the
    paper's own self-disclosure pipeline already treats as equivalent
    (hamza-bearing alef forms, taa marbuta / haa)."""
    text = unicodedata.normalize("NFKC", text)
    text = ARABIC_DIACRITICS.sub("", text)
    text = re.sub(r"[إأآٱ]", "ا", text)
    text = text.replace("ى", "ي")
    text = text.replace("ة", "ه")
    return text


def tokenize(text):
    text = normalize_arabic(text)
    return [t for t in TOKEN_RE.findall(text) if len(t) >= 2]


def load_stopwords(path=STOPWORDS_PATH):
    """Arabic stopword list (one word per line), normalized the same way as
    corpus tokens so they match regardless of presentation-form variants."""
    with open(path, encoding="utf-8") as f:
        words = (normalize_arabic(line.strip()) for line in f if line.strip())
        return {w for w in words if w}


# ---------------------------------------------------------------------------
# Morphological first-person / negation tagging
# ---------------------------------------------------------------------------
#
# Cascade per token: MSA MLE disambiguator (context-aware) -> Egyptian MLE
# disambiguator (context-aware) -> Gulf morphology-db (no disambiguator
# ships for Gulf, so we accept a hit from *any* candidate analysis) ->
# FALLBACK_NEGATION_TOKENS exact match. A token counts as first-person/
# negation if *any* tier flags it -- each tier's criterion is specific
# enough (a particular POS+feature combination) that a wrong-but-lexical
# analysis from an unrelated dialect essentially never spuriously matches.

_MLE_MSA = None
_MLE_EGY = None
_AN_GLF = None


def _load_taggers():
    global _MLE_MSA, _MLE_EGY, _AN_GLF
    if _MLE_MSA is None:
        _MLE_MSA = MLEDisambiguator.pretrained("calima-msa-r13")
        _MLE_EGY = MLEDisambiguator.pretrained("calima-egy-r13")
        _AN_GLF = CamelAnalyzer(MorphologyDB.builtin_db("calima-glf-01"))


def is_first_person(analysis):
    """True if this single morphological analysis carries first-person
    subject agreement (pronoun/verb) or a first-person object/possessive
    clitic."""
    if analysis.get("pos") in ("pron", "verb") and analysis.get("per") == "1":
        return True
    for slot in ("enc0", "enc1", "prc0", "prc1", "prc2", "prc3"):
        v = str(analysis.get(slot, "0"))
        if v.startswith("1s_") or v.startswith("1p_"):
            return True
    return False


def is_negation(analysis):
    """True if this analysis is a negation particle, or carries a negation
    proclitic (e.g. Egyptian circumfix mA_neg...(-sh))."""
    if analysis.get("pos") == "part_neg":
        return True
    for slot in ("prc0", "prc1", "prc2", "prc3", "enc0", "enc1"):
        if "neg" in str(analysis.get(slot, "0")).lower():
            return True
    return False


@lru_cache(maxsize=200_000)
def _glf_flags(token):
    """Gulf morphology-db has no scored disambiguator, so pool over every
    candidate analysis. Cached per token since it's context-independent."""
    analyses = _AN_GLF.analyze(token)
    return (any(is_first_person(a) for a in analyses),
            any(is_negation(a) for a in analyses))


def tag_post(text):
    """Tokenize and tag a single post, returning (n_first_person,
    n_negation, n_tokens)."""
    _load_taggers()
    toks = tokenize(text)
    if not toks:
        return 0, 0, 0

    msa = _MLE_MSA.disambiguate(toks)
    egy = _MLE_EGY.disambiguate(toks)

    n_fp = n_neg = 0
    for i, tok in enumerate(toks):
        a_msa = msa[i].analyses[0].analysis
        a_egy = egy[i].analyses[0].analysis
        fp = is_first_person(a_msa) or is_first_person(a_egy)
        neg = is_negation(a_msa) or is_negation(a_egy) or tok in FALLBACK_NEGATION_TOKENS
        if not (fp and neg):
            g_fp, g_neg = _glf_flags(tok)
            fp = fp or g_fp
            neg = neg or g_neg
        n_fp += fp
        n_neg += neg
    return n_fp, n_neg, len(toks)


def _tag_post_worker(text):
    return tag_post(text)


def morphological_marker_rates(posts_df, n_workers=None):
    """Per-1,000-token first-person and negation rates for a group, tagged
    post-by-post via the morphological cascade above (multiprocessed --
    this is the slow step in the script, roughly 1k tokens/sec/core)."""
    n_workers = n_workers or cpu_count()
    texts = posts_df["text"].tolist()

    n_fp = n_neg = n_tok = 0
    with Pool(n_workers, initializer=_load_taggers) as pool:
        for fp, neg, tok in tqdm(pool.imap(_tag_post_worker, texts, chunksize=200),
                                  total=len(texts), desc="Morphological tagging"):
            n_fp += fp
            n_neg += neg
            n_tok += tok

    return {
        "first_person_rate_per_1k": n_fp / n_tok * 1000 if n_tok else 0.0,
        "negation_rate_per_1k": n_neg / n_tok * 1000 if n_tok else 0.0,
    }


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_groups():
    print("Loading preprocessed posts …")
    pre = pd.read_csv(PREPROCESSED, keep_default_na=False, usecols=["user_id", "text"])
    pre = pre[pre["text"].str.strip() != ""]

    print("Loading split manifest …")
    manifest = pd.read_csv(SPLIT_MANIFEST, keep_default_na=False)

    diagnosed_users = set(manifest.loc[manifest["y"] == 1, "user_id"])
    control_users = set(manifest.loc[manifest["y"] == 0, "user_id"])
    overlap = diagnosed_users & control_users
    if overlap:
        print(f"  WARNING: {len(overlap)} users appear as both diagnosed and control; dropping from both.")
        diagnosed_users -= overlap
        control_users -= overlap

    print(f"  {len(diagnosed_users):,} diagnosed users, {len(control_users):,} control users")

    diag_posts = pre[pre["user_id"].isin(diagnosed_users)]
    ctrl_posts = pre[pre["user_id"].isin(control_users)]
    print(f"  {len(diag_posts):,} diagnosed posts, {len(ctrl_posts):,} control posts")

    return diag_posts, ctrl_posts


# ---------------------------------------------------------------------------
# 1. Log-odds-ratio with informative Dirichlet prior
# ---------------------------------------------------------------------------

def log_odds_dirichlet(counts_a, counts_b, background_counts, user_counts_a, user_counts_b,
                        min_freq=MIN_TOKEN_FREQ, min_users=MIN_USER_FREQ, stopwords=frozenset()):
    """Monroe, Colaresi & Quinn (2008), 'Fightin' Words'. Positive z-scores
    are distinctively over-used by group A relative to B; negative by B
    relative to A. The combined (a+b) corpus is used as the background
    prior, scaled by DIRICHLET_ALPHA0_SCALE. Stopwords are excluded from the
    ranked vocabulary so they can't surface as "keywords".

    A token is also dropped if, in whichever group it has nonzero count,
    that count is contributed by fewer than min_users distinct users --
    otherwise a single prolific/repetitive poster can look like a
    group-level "keyword" (e.g. one user posting the same phrase 190
    times)."""
    vocab = [w for w, c in background_counts.items()
             if c >= min_freq and w not in stopwords]
    n_a = sum(counts_a.values())
    n_b = sum(counts_b.values())
    alpha0 = DIRICHLET_ALPHA0_SCALE * sum(background_counts.values())

    rows = []
    for w in vocab:
        y_a = counts_a.get(w, 0)
        y_b = counts_b.get(w, 0)
        u_a = user_counts_a.get(w, 0)
        u_b = user_counts_b.get(w, 0)
        if (y_a > 0 and u_a < min_users) or (y_b > 0 and u_b < min_users):
            continue
        a_w = DIRICHLET_ALPHA0_SCALE * background_counts[w]

        delta = (np.log((y_a + a_w) / (n_a + alpha0 - y_a - a_w))
                 - np.log((y_b + a_w) / (n_b + alpha0 - y_b - a_w)))
        variance = 1.0 / (y_a + a_w) + 1.0 / (y_b + a_w)
        z = delta / np.sqrt(variance)
        rows.append((w, y_a, y_b, u_a, u_b, delta, z))

    return pd.DataFrame(rows, columns=["token", "count_a", "count_b", "n_users_a", "n_users_b", "log_odds", "z"])


# ---------------------------------------------------------------------------
# 2. Summary statistics
# ---------------------------------------------------------------------------

def type_token_ratio(tokens, sample_size, seed):
    """TTR on a fixed-size random subsample so it's comparable across groups
    with very different total token counts."""
    rng = np.random.default_rng(seed)
    if len(tokens) > sample_size:
        idx = rng.choice(len(tokens), size=sample_size, replace=False)
        tokens = [tokens[i] for i in idx]
    return len(set(tokens)) / len(tokens)


def marker_rate(counts, marker_set):
    total = sum(counts.values())
    hits = sum(c for w, c in counts.items() if w in marker_set)
    return hits / total * 1000  # per 1,000 tokens


def summarize_group(posts_df, seed, ttr_sample_size):
    all_tokens = []
    post_lengths = []
    user_counts = Counter()  # per-token count of distinct users who used it
    for _, user_posts in posts_df.groupby("user_id")["text"]:
        user_tokens = set()
        for text in user_posts:
            toks = tokenize(text)
            all_tokens.extend(toks)
            post_lengths.append(len(toks))
            user_tokens.update(toks)
        user_counts.update(user_tokens)

    counts = Counter(all_tokens)
    stats = {
        "n_posts": len(posts_df),
        "n_tokens": len(all_tokens),
        "ttr": type_token_ratio(all_tokens, ttr_sample_size, seed),
        "mean_tokens_per_post": float(np.mean(post_lengths)) if post_lengths else 0.0,
        "first_person_rate_per_1k": marker_rate(counts, FIRST_PERSON_TOKENS),
        "negation_rate_per_1k": marker_rate(counts, NEGATION_TOKENS),
    }
    return stats, counts, user_counts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/lexsem_diagnosed_vs_control.csv")
    parser.add_argument("--top-k", type=int, default=15,
                         help="Number of top diagnosed-/control-associated terms to report")
    parser.add_argument("--ttr-sample-size", type=int, default=500_000,
                         help="Tokens subsampled per group for the type-token ratio")
    parser.add_argument("--min-user-freq", type=int, default=MIN_USER_FREQ,
                         help="Minimum distinct users in a group required for a token's "
                              "count there to count towards the log-odds ranking")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    diag_posts, ctrl_posts = load_groups()

    print("\nComputing summary statistics …")
    diag_stats, diag_counts, diag_user_counts = summarize_group(diag_posts, RANDOM_SEED, args.ttr_sample_size)
    ctrl_stats, ctrl_counts, ctrl_user_counts = summarize_group(ctrl_posts, RANDOM_SEED, args.ttr_sample_size)

    stats_df = pd.DataFrame([
        {"group": "diagnosed", **diag_stats},
        {"group": "control", **ctrl_stats},
    ])
    print(stats_df.to_string(index=False))

    stopwords = load_stopwords()
    print(f"\nLoaded {len(stopwords):,} Arabic stopwords to exclude from keyword ranking …")

    print("Computing log-odds-ratio with Dirichlet prior (diagnosed vs. control) …")
    background_counts = diag_counts + ctrl_counts
    lo = log_odds_dirichlet(diag_counts, ctrl_counts, background_counts,
                             diag_user_counts, ctrl_user_counts,
                             min_users=args.min_user_freq, stopwords=stopwords)
    lo = lo.sort_values("z", ascending=False)

    top_diag = lo.head(args.top_k)
    top_ctrl = lo.tail(args.top_k).sort_values("z")

    print(f"\nTop {args.top_k} diagnosed-associated terms:")
    print(top_diag.to_string(index=False))
    print(f"\nTop {args.top_k} control-associated terms:")
    print(top_ctrl.to_string(index=False))

    stats_df.to_csv(output, index=False)
    lo_path = output.with_name(output.stem + "_log_odds.csv")
    lo.to_csv(lo_path, index=False)
    print(f"\nSaved summary stats to {output}")
    print(f"Saved full log-odds ranking to {lo_path}")


if __name__ == "__main__":
    main()
