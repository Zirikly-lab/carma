# Classification Experiments

Implements the two binary classification experiments described in the paper
(§7 Experiments): classical TF-IDF classifiers (post-level) and fine-tuned
Arabic PLMs (user-level). Both are per-condition, binary (diagnosed vs.
control), balanced 1:1.

## Status

- [x] Data prep: shared, user-level, balanced train/test split — done, reviewed for sample sizes, **awaiting sign-off** before wiring it into the experiment scripts.
- [ ] Update `classical.py` / `finetune.py` to consume the split manifest below (currently each script independently re-derives its own split — see "Known gap" below).
- [ ] Re-run experiments and refresh `results/`.

## Data source

`data/posts/v1/reddit-preprocessed.csv` — post-level: `user_id`, `class`, `text`.
This is the raw pattern-pipeline output, 9,149 users. It is **larger** than the
curated 3,080-user corpus reported in the paper (no additional filtering has
been applied here yet), so treat counts below as upper bounds on what's usable,
not the published corpus.

## Data prep: `data_prep.ipynb`

Single notebook, run top to bottom, no model training. Produces the split
manifest consumed by both experiment scripts.

**Why not use `class` directly as the label:** `class` is assigned per *post*,
not per *user*. For a diagnosed user, only the post(s) that matched the
self-disclosure pattern carry the condition label; the rest of that user's
retrieved history (posts that never matched a pattern) come through as
`control` or blank. Taking `class` at face value would leak a diagnosed user's
own non-matching posts into the control class. The notebook checked this
directly: 333 users carry more than one distinct `class` value across their
posts, and in every one of those cases it's exactly "one real condition +
control/blank filler" — never two distinct real conditions. So labels are
collapsed to one per user:

1. any post has a real condition → that condition
2. else any post is explicitly `control` → `control`
3. else (every post blank) → `unknown`, **excluded** (662 users; not assumed
   control, since they never got an explicit `control` stamp)

**Balancing:** for each condition, `n = min(n_positive, n_control_available)`
control users are sampled without replacement (seed 42); control users can be
reused across different conditions' splits, but never appear as both `train`
and `test` within the same condition.

**Split:** positive and sampled-control sets are each split 90/10 at the user
level independently (so both train and test stay 1:1 balanced), seed 42.
Sanity-checked in the notebook: zero leakage (no user in both splits for a
condition), exact 1:1 balance in every train/test cell.

To rerun:

```bash
source .venv/bin/activate
jupyter nbconvert --to notebook --execute --inplace experiments/data_prep.ipynb
```

## Sample sizes available (`../data/splits/sample_sizes.csv`)

Minimum 30 positive users required to include a condition (`MIN_USERS` in the
notebook). 13 of 18 conditions clear the bar:

| condition | n users | included |
|---|---|---|
| depression | 1,831 | yes |
| anxiety | 644 | yes |
| adhd | 643 | yes |
| sleep_disorder | 357 | yes |
| ocd | 311 | yes |
| autism | 227 | yes |
| panic | 147 | yes |
| bpd | 98 | yes |
| ptsd | 92 | yes |
| suicidal | 80 | yes |
| bipolar | 76 | yes |
| schizophrenia | 45 | yes |
| eating_disorder | 41 | yes |
| paranoid_pd | 24 | no (< 30) |
| did | 11 | no (< 30) |
| trichotillomania | 9 | no (< 30) |
| narcissistic_pd | 3 | no (< 30) |
| avoidant_pd | 3 | no (< 30) |

Control pool available: 3,845 users — large enough to cover every condition's
1:1 balance requirement without exhausting it.

## Split manifest (`../data/splits/condition_user_splits.csv`)

9,184 rows, one per `(condition, user_id)` pair used in that condition's
experiment:

| column | meaning |
|---|---|
| `condition` | one of the 13 included conditions |
| `user_id` | Reddit username |
| `y` | 1 = diagnosed with `condition`, 0 = control |
| `split` | `train` or `test` |

This is deliberately lightweight (no post text) — downstream scripts join it
back to `reddit-preprocessed.csv` by `user_id`:

- **classical.py**: explode each `(condition, user_id, split)` row to that
  user's posts, label inherited from the user, TF-IDF at the post level.
- **finetune.py**: concatenate each user's posts into one sequence, classify
  at the user level.

## Known gap

`classical.py` and `finetune.py` currently each independently re-derive their
own train/test split and balancing (different sampling mechanics per script —
`rng.choice` vs. `df.sample`), so as they stand today there's no guarantee
they train/test on the same users for a given condition, and neither goes
through the label-collapsing logic above (both instead re-label via
`data/metadata/majority-vote-reddit.csv`, a subset tied to the now-appendix
LLM-as-Judge exploratory analysis, not the pattern-pipeline-only corpus the
paper now describes). Next step, pending sign-off on the split above: point
both scripts at `data/splits/condition_user_splits.csv` instead so classical
and PLM results are directly comparable and reproduce the same corpus
definition used in the paper.

## Scripts

- `data_prep.ipynb` — this step.
- `classical.py` — TF-IDF + {NB, LR, SVM, XGBoost}, post-level. `run_classical.sh` (SLURM/CPU).
- `finetune.py` — AraBERT-Twitter / CAMeLBERT fine-tuning, user-level. `run_finetune.sh` (SLURM/GPU).
- `finetuning.py` — stale duplicate of `finetune.py`, unused.
