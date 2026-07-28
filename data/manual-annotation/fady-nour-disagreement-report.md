# Fady vs. Nour disagreement — root-cause analysis

## Data-integrity note (read this first)

`agreement-results-v2.md` (already in the repo) reports **Fady vs. Nour κ = 0.641**,
which is almost certainly the "kappa 0.6" figure being referenced. Two problems with
that number:

1. **The checked-in `agreement.py` is currently broken.** Line 30 does
   `fady[["id", "diagnosis", "fad_label"]].rename(columns={"Label": "fady"})` —
   it selects `fad_label` but renames a column called `"Label"`, which doesn't
   exist in `fady-v2.csv`. Running it raises `KeyError: 'fady'`; it cannot have
   produced `agreement-results-v2.md` as currently written.
2. **Recomputing by hand from the current `fady-v2.csv` / `nour-v2.csv` on disk**
   (merging on `id`, restricting to rows where both gave `TP`/`FP`) gives a very
   different result:

   | | reported in `agreement-results-v2.md` | recomputed from current CSVs |
   |---|---|---|
   | n | 254 | 255 |
   | Fady TP/FP | 177 / 77 | 148 / 107 |
   | % agree | 85.8% | 54.5% |
   | Cohen's κ | 0.641 | **0.004** (chance level) |

   The label counts don't match either, so the CSVs on disk have different
   annotations than whatever produced that report. **The current files
   disagree far more than κ=0.6** — the "0.6" figure appears stale. Everything
   below uses the live data on disk, verified row-by-row (text content for
   each `id` matches between the two files, so the merge/join itself is correct
   — the labels really do disagree this much).

Recommend: fix the one-line bug, re-run `agreement.py`, and regenerate
`agreement-results-v2.md` so the checked-in report matches the checked-in data.

## Headline numbers (live data, n=255 rows both labeled TP/FP)

- % raw agreement: 54.5% | Cohen's κ: 0.004
- Fady calls TP 58.0% of the time; **Nour calls TP 76.9%** of the time (only
  23% FP). Nour's label distribution is far more skewed toward TP than
  Fady's, which is the single biggest driver of the disagreement.
- Disagreement is **directional and lopsided**: 82 rows where Fady says FP /
  Nour says TP, vs. only 34 rows the other way around.

## Disagreement is concentrated in specific categories, not spread evenly

| diagnosis | n | agree% | Fady=FP,Nour=TP | Fady=TP,Nour=FP |
|---|---|---|---|---|
| sleep_disorder | 19 | **15.8%** | 16 | 0 |
| eating_disorder | 20 | **25.0%** | 13 | 2 |
| bipolar | 20 | 30.0% | 9 | 5 |
| suicidal | 20 | 40.0% | 10 | 2 |
| anxiety | 18 | 44.4% | 9 | 1 |
| ptsd | 20 | 55.0% | 7 | 2 |
| autism | 20 | 60.0% | 0 | 8 |
| bpd | 19 | 63.2% | 4 | 3 |
| schizophrenia | 20 | 65.0% | 3 | 4 |
| depression | 20 | 70.0% | 3 | 3 |
| adhd | 19 | 73.7% | 3 | 2 |
| panic | 20 | 80.0% | 2 | 2 |
| ocd | 20 | 85.0% | 3 | 0 |

`sleep_disorder` and `eating_disorder` alone account for 29 of the 116
disagreements, **entirely in the "Nour says TP, Fady says FP" direction**.
`autism` is the mirror image — 8/8 of its disagreements go the *other* way
(Fady TP, Nour FP), and it's the **only** category where Fady is the more
lenient one.

## Three distinct causes, with examples

### 1. Fady FP's unambiguous first-person self-reports (sleep/eating/bipolar)

These aren't borderline calls — by the guidelines' own definition ("انا عندي
اكتئاب" is the canonical TP example), these should be clear TPs, but Fady
marked them FP anyway:

> **id `1leyggi`** (sleep_disorder) — *"عندي ارق"* ("I have insomnia.")
> Fady: FP · Nour: TP. Three words, direct, unhedged. No sarcasm, no
> third-person, no negation — textbook TP per the guidelines, yet Fady
> called it FP.

> **id `1io77uj`** (sleep_disorder) — *"عندي insomnia ونفسي انام مصحاش"*
> ("I have insomnia and I want to sleep, I can't.") Fady: FP · Nour: TP.

> **id `1qv6252`** (eating_disorder) — *"أنا عندي Eating disorder ووزني
> زايد مؤخراً حوالي ٣٠ كيلو... جربت في ألف دايت"* ("I have an eating
> disorder, I've gained ~30kg recently... tried a thousand diets.")
> Fady: FP · Nour: TP. Explicit self-identification plus corroborating
> detail (weight gain, failed diets, medical concerns).

> **id `1cqvqwq`** (bipolar) — long first-person post ending *"...احا انا
> عندي ثنائي القطب وده بيتورث"* ("...I have bipolar disorder and it's
> hereditary") in a post about suicidal ideation. Fady: FP · Nour: TP.

This looks like a real annotation inconsistency, not genuine ambiguity —
Fady appears to apply a stricter, more clinical bar to these three
categories specifically (maybe treating common colloquial complaints like
"insomnia" or "diet struggles" as too mundane to count) while accepting the
identical pattern ("عندي X") for other diagnoses.

### 2. Hedged / tentative self-diagnosis language — genuine interpretive fork

Here the two annotators are applying different (defensible) thresholds for
how confident a self-report has to be, mostly in `bpd`, `schizophrenia`,
`ptsd`:

> **id `1ipibvc`** (bpd) — *"شاكه ان عندي اضطراب الشخصية الحدية"*
> ("I **suspect** I have BPD...") Fady: TP · Nour: FP. Fady credits the
> hedge as still a self-report; Nour treats "suspect" as not confirmed
> enough.

> **id `1pbt9t6`** (bpd) — *"واحدة اعرفها قالتلي انها شاكة أن عندي bpd...
> بس هما مش عارفين... كل حاجة تنطبق عليا"* ("A friend told me she suspects
> I have BPD... but they don't really know... everything applies to me.")
> Fady: TP · Nour: FP — third-hand + self-doubt, genuinely borderline.

> **id `1efs7wv`** (schizophrenia) — *"...و الوقتي شاكه انه ممكن يكون
> عندي فصام كمان"* ("...right now I suspect I might have schizophrenia
> too") in a post listing prior formal diagnoses (depression, OCD, BPD).
> Fady: TP · Nour: FP.

These are exactly the kind of cases the guidelines' `NA` label exists for
("matched the algorithm but can't confidently call TP or FP") — but the
current pipeline is being scored as forced binary TP/FP, so legitimate
uncertainty shows up as raw disagreement.

### 3. Sarcasm / hyperbole that only Nour catches (autism)

`autism` is where Fady, not Nour, is the systematically wrong one:

> **id `1kdbrb7`** (autism) — *"تومب رايدر... ختمتهم اكثر من خمس مرات
> وجاني جنون اشك انه صار فيني توحد من كثير ماحفظت الألغاز"* ("I've beaten
> Tomb Raider 5+ times, I think I got autism from memorizing all the
> puzzles.") Fady: TP · Nour: FP. Joking self-deprecation about a video
> game, not a real symptom report — Nour catches the joke, Fady misses it.
> (This exact post was already flagged in `README.md` as a case where the
> LLMs also missed the joke — so three of four annotators/models get this
> one wrong.)

## Why κ is worse than raw % agreement suggests

Because Nour predicts TP 76.9% of the time and Fady 58.0%, a large chunk of
apparent "agreement" would happen by chance alone even if the two were
labeling randomly — Cohen's κ corrects for that and exposes it. With κ≈0.00,
the current Fady/Nour labels are statistically indistinguishable from two
annotators who agree only because they're both biased toward the majority
class, not because they're applying the same criteria.

## Recommendations

1. Fix `agreement.py`'s column-rename bug and regenerate
   `agreement-results-v2.md` so it reflects the real data (κ≈0.00, not 0.641).
2. Adjudicate the 29 `sleep_disorder`/`eating_disorder` disagreements first —
   they look like clear Fady mislabels against the existing guidelines, not
   ambiguous cases, and fixing them alone would meaningfully raise κ.
3. Clarify the guidelines on hedged self-diagnosis ("شاكه", "ممكن يكون
   عندي") — decide explicitly whether "suspect I have X" is TP or NA, since
   Fady and Nour are currently resolving it in opposite directions.
4. Re-review the `autism` category for sarcasm/hyperbole ("عندي توحد" used
   as a joke) specifically with Fady, since it's the one category where
   Fady, not Nour, is the outlier.
