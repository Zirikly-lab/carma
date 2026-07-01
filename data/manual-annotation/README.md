# Manual vs. LLM Annotation

Two humans (Fady, Nour) and two LLMs (Qwen2-72B, Jais) independently labeled the
same 260-post Reddit sample, each choosing one of three labels for whether a
post is a genuine self-report of the `diagnosis` condition:

| Label | Meaning |
|---|---|
| `TP` | Author genuinely appears to have the condition (symptoms, meds, or a sincere self-report — no formal diagnosis required). |
| `FP` | Clear mismatch: sarcasm, talking about someone else, figurative use, negation, news content, etc. Not for weak/uncertain cases. |
| `NA` | Matched the keyword algorithm but the annotator can't confidently call TP or FP. Meant to be used sparingly, after trying TP/FP first. |

Full label definitions: [`guidelines.txt`](guidelines.txt).

## Files

| File | Annotator | Label column |
|---|---|---|
| `reddit-sample-fady.csv` | Fady (manual) | `Label` |
| `reddit-sample-nour.csv` | Nour (manual) | `nour_label` |
| `reddit-sample-qwen.csv` | Qwen2-72B (LLM) | `annotation` |
| `reddit-sample-jais.csv` | Jais (LLM) | `annotation` |
| `agreement.py` | Computes pairwise % agreement, Cohen's κ, per-label P/R/F1, confusion matrices, and 4-way agreement over the merged set. Run with `python3 data/manual-annotation/agreement.py`. |
| `manual_annotation.py` / `annotate.sh` / `annotate_jais.sh` | Scripts used to produce the Qwen / Jais LLM labels via vLLM. |
| `manual-annotation.ipynb` | Notebook used for the manual annotation pass. |

## Agreement summary

Computed by `agreement.py` over rows where both annotators in the pair have a
valid label (`TP`/`FP`/`NA`; `NONE`/`PARSE_FAIL` rows excluded).

| Pair | n | % agree | Cohen's κ |
|---|---|---|---|
| Fady vs. Nour (human vs. human) | 251 | 75.3% | 0.480 |
| Qwen vs. Jais (LLM vs. LLM) | 258 | 75.6% | 0.190 |
| Fady vs. Qwen | 259 | 73.0% | 0.198 |
| Fady vs. Jais | 258 | 71.3% | 0.196 |
| Nour vs. Qwen | 250 | 62.8% | 0.155 |
| Nour vs. Jais | 249 | 63.5% | 0.197 |
| **All four agree** | 249 | **51.0%** | — |

Takeaways:
- Raw % agreement looks similar across every pair (63–76%), but **κ tells a
  different story**: the two humans agree far more than chance (κ=0.48)
  while every human↔LLM and LLM↔LLM pair sits around κ≈0.15–0.20 (only
  slightly better than chance). The label distributions are skewed toward
  `TP`, which inflates raw % agreement for pairs that both over-predict `TP`.
- `NA` is the least reliable label everywhere — F1 between any two
  annotators on `NA` is 10–38%, i.e. one annotator's "not sure" rarely
  matches another's.
- Both LLMs predict `TP` much more readily than the humans (Qwen: 218 `TP`,
  Jais: 209 `TP`, vs. Fady: 198, Nour: 158) and use `NA`/`FP` far less
  (Qwen/Jais `NA` counts: 15/12 vs. Fady/Nour: 24/49). The LLMs resolve
  ambiguity toward `TP` where humans hedge toward `NA`.

## Sample: where everyone agrees

**All four agree — `TP`** (123/249 rows, the bulk of full agreement):

> `adhd` — *"السلام عليكم أنا عندي adhd ونسيت حبوبي حابة اعرف إذا في عيادة تصرف vyvanse 10mg or Adderall 5mg…"*
> id `1mfm0pv` — a direct, first-person medication question. Unambiguous self-report.

**All four agree — `FP`** (only 4/249 rows — full FP agreement is rare):

> `autism` — *"صحيح انا عندي اخ معاه توحد وكانو يقولون لنا ودوه عند احد يكويه في راسه 😀"*
> id `1cdjn3b` — third-person ("my brother has autism"), plus a sarcastic tag. Easy FP for every annotator.

## Sample: where annotators disagree the most

The most common disagreement patterns (fady / nour / qwen / jais), by count:

| Pattern | n | Reading |
|---|---|---|
| TP / NA / TP / TP | 15 | Nour alone hedges to NA; everyone else says TP |
| FP / FP / TP / TP | 9 | **Humans agree FP, both LLMs say TP** |
| TP / TP / FP / TP | 9 | Both humans + Jais say TP; Qwen alone says FP |
| TP / TP / TP / FP | 9 | Both humans + Qwen say TP; Jais alone says FP |
| TP / FP / TP / TP | 8 | Nour alone says FP; everyone else says TP |
| NA / NA / TP / TP | 8 | **Both humans hedge to NA, both LLMs confidently say TP** |
| TP / NA / TP / FP | 8 | Fady/Qwen say TP; Nour NA, Jais FP — no consensus |

The two rows worth reading closely — they show the systematic human/LLM
split, not just noise:

**Humans say `FP`, both LLMs say `TP`** (9 rows) — LLMs read hypothetical /
identification-with-a-symptom language as a genuine self-report where humans
correctly caught it as speculative or about someone else:

> `autism` — *"يسطا صدقني دور في الموضوع وحاول تروح لدكتور نفساني، لو اتشخصت بالتوحد دا هيفهمك حاجات كتييييير اوي…"*
> id `1fjx0zn` — the poster is advising *someone else* to go get checked for autism; not a self-report.

> `autism` — *"تومب رايدر النسختين ختمتهم اكثر من خمس مرات وجاني جنون اشك انه صار فيني توحد من كثير ماحفظت الألغاز…"*
> id `1kdbrb7` — joking self-deprecation about replaying a video game too much ("I think I got autism from memorizing all the puzzles"), not a real symptom report. Both LLMs miss the joke.

**Both humans hedge to `NA`, both LLMs confidently say `TP`** (8 rows) — LLMs
resolve ambiguous/uncertain self-report language ("شاكه", "احتمال يكون
عندي") toward TP, where humans correctly flagged it as too uncertain to call:

> `bpd` — *"حبيبي أنا احتمال يكون عندي bpd ف اذا جد عندي بدي علاج سلوكي وصلت؟"*
> id `1msyvbb` — "I might have BPD" — tentative, hedged language; humans said NA, both LLMs called it TP outright.

> `bpd` — *"حد يعرف اي دكتور نفسي كويس…شاكه ان عندي اضطراب الشخصية الحدية…"*
> id `1ipibvc` — "I suspect I have BPD" (شاكه = suspecting), same pattern.

**Qwen and Jais disagree with each other even when both humans agree on `TP`**
(9 rows each direction) — these look like LLM-specific parsing/precision
failures rather than genuinely ambiguous posts:

> `adhd` — *"طيب هو ماكذب انا عندي adhd وهيك فيديوهات اشوف بس اول خمس دقايق وامل 🤣🤣🤣🤣"*
> id `1i5oltv` — humans + Jais say TP (genuine ADHD self-report, joking tone about attention span); Qwen alone calls it FP, likely thrown off by the humor/emoji.

> `anxiety` — *"مش بعرف يخويا عندي رهاب اجتماعي"*
> id `1mz56x1` — a short, direct social-anxiety self-report; humans + Qwen say TP, Jais alone calls it FP for no obvious reason — likely a Jais precision issue on short posts.

## Reproducing this analysis

```bash
python3 data/manual-annotation/agreement.py
```

The examples above were pulled by merging the four CSVs on `id`, restricting
to rows where all four annotators produced a valid label (n=249), and
filtering by exact label-tuple patterns (see `agreement.py`'s
`load_data()`/`main()` for the merge logic this reuses).
