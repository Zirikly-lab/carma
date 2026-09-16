# CARMA: ARR → ICWSM Action Plan

Source manuscript: `arr/ARRv3.tex` (ACL format). Reviews: `icwsm/arr-reviews.md` (3 ARR
reviews, all "Resubmit"/"Borderline"). Manuscript: `icwsm/CARMA.tex` (AAAI format, per
`icwsm/aaai-template/`). Compiled PDF: `icwsm/CARMA.pdf`.

**Status: manuscript text is final.** All reviewer-raised content items are resolved,
per your explicit calls on the ones with real judgment calls (see below). No open
placeholders, warnings, or TODO markers remain in the compiled text.

## 1. Resolution log (reviewer items + your explicit corrections)

1. **TP/FP only, no NA label.** You corrected an earlier pass of mine that had (based
   on the raw annotation files) added an NA label back into the paper. Per your
   explicit instruction, NA is irrelevant and must never appear — reverted completely.
   The annotation scheme throughout `CARMA.tex` (§3.1 Human Annotation, Appendix G
   guidelines) is now TP/FP only, matching your intent, not what the raw
   `data/manual-annotation/` files technically contain.
2. **"High precision" framing vs. 21.7% FP rate.** Reworded to "precision-oriented" in
   Abstract/Intro/Dataset Construction, with a justification sentence after the FP-rate
   estimate in §3.1.
3. **"Diagnosed"/"control" terminology.** Kept current terms per your choice; added a
   defining footnote at first use (Introduction) pointing to §3.2.
4. **LLM classification baseline — declined**, out of scope for the ICWSM timeline per
   your call.
5. **40-character co-occurrence window.** Cited SMHD's own $F_{0.5}$-optimization
   result as the justification (§Dataset Construction).
6. **Control-group construction / matched sampling.** Added a Limitations sentence:
   SMHD/MINDSET could afford matched sampling given English Reddit's larger candidate
   pool; the Arabic-speaking subreddit ecosystem is too small for that here.
7. **Release plan.** Ethical Considerations now states plainly that the released
   corpus is post-level text with Reddit usernames replaced by irreversibly hashed
   pseudonymous identifiers, DUA-gated. Per your instruction, all references to the
   internal `reddit-preprocessed.csv` filename and the in-text engineering-TODO warning
   have been removed from the paper — the statement now reads as final policy, not a
   flagged open question. **Operationally** (outside the paper text): the actual
   `user_id` column in `data/posts/v1/reddit-preprocessed.csv` has not been hashed yet
   — that's still a real data-pipeline step to do before the described release policy
   is literally true of the data on disk. Not blocking the manuscript; flagging here so
   it isn't lost now that it's no longer flagged in-paper.
8. **Post-history temporal validity.** Added a "Temporal Validity of Posting History"
   Limitations paragraph (no fabricated stat — the corpus's own retained fields don't
   support one).
9. **Recall inflating F1.** Added a fourth interpretive point in §Results tracing the
   actual mechanism (`experiments/classical.py`'s user-level-only balancing plus
   diagnosed users posting ~1.7–2.6x more per user than control users on average).
10. **Dual-use / surveillance risk.** Added a "Dual-Use Risk" paragraph to Ethical
    Considerations (MENA-specific stigma/legal context, concrete mitigations).
11. **PLM truncation caveat.** Added an "Input Truncation in PLM Baselines" Limitations
    paragraph.
12. **Dialect-ID model validation.** Added a citation to the original model's reported
    strength on the NADI benchmark plus an honest domain-shift caveat (no fabricated
    accuracy number — couldn't extract one from the source PDF in this environment).
13. **Mechanical fixes + 2 issues found during a QA pass against the actual
    figures/data:**
    - Typos fixed (FastText, "fewer than," Reddit API).
    - Appendix C keyword-table caption fixed to explain the 15-vs-12-condition split
      (this was the same "caption says 12, table shows 15" issue R1 flagged, just in a
      different table than the one R1 pointed at).
    - Dialect figure/text mismatch fixed: text now says 56.1% Egyptian, matching the
      actual rendered figure (was 55.75%).
    - **Table 2 control row:** I had added a Control row computed from
      `reddit-preprocessed.csv` (4,080 users / 264,469 posts), which disagreed with the
      "2,875 control users" figure used everywhere else in the paper. Per your
      instruction, **2,875 is the only correct control-user count** — the added row and
      its discrepancy warning have been removed entirely; Table 2 is back to only the
      12 diagnosed conditions, and "2,875" is the sole control-count figure anywhere in
      the paper (Abstract, §3.4, Conclusion).
14. **MINDSET citation.** Already cited (`mankarious2025mindset`) in Related Work and
    Limitations; made the Related Work mention explicitly name "MINDSET" (previously
    only cited, not named, there) for parity with how SMHD is introduced.
15. **Paper Checklist placement.** Moved from the end of the appendices to its own
    section immediately after `\bibliography{custom}` and before `\appendix` — it is no
    longer a lettered appendix. All `\answerTODO{Answer}` placeholders have been
    replaced with genuine, referenced answers (`\answerYes`/`\answerNo`/`\answerNA`)
    based on what the manuscript actually says — including honest `No`s where the paper
    doesn't cover something (compute budget, error bars across seeds, asset licenses,
    annotator compensation, a formal Datasheet/FAIR discussion), rather than
    overclaiming coverage.

## 2. ICWSM/AAAI formatting — still open

- **Compiles cleanly.** Verified end-to-end on this cluster (`module load texlive/2020`
  → `xelatex → bibtex → xelatex → xelatex`): all citations and cross-references
  resolve, 18 pages, no errors. `icwsm/CARMA.pdf` is current as of this compile.
  Compiled locally with `Amiri` substituted for `Noto Sans Arabic` (the latter isn't
  installed on this cluster) — **the checked-in `CARMA.tex` still specifies Noto Sans
  Arabic**; only the local preview PDF used the substitute. Confirm Noto Sans Arabic is
  available wherever you compile for submission, or decide to switch permanently.
- **`\resizebox` on tables is disallowed by AAAI.** 4 tables still use it (full
  classical/PLM results, the two phrase-inventory tables) and one overflows the page by
  ~293pt as a result (seen in the compile log). Needs reformatting before submission.
- **Non-Roman script restriction.** AAAI's camera-ready text says non-Latin scripts
  "must be restricted to bit-mapped figures." Needs checking against the actual current
  ICWSM author kit (not assumed from this generic AAAI kit) before spending effort
  converting the paper's many inline Arabic examples to images.
- **Figures.** Paper references `latex/figures/fig_*.png`; real files are at
  `data/posts/v1/fig_*.png`. Fine for local compiling (I mirror them into a scratch
  `latex/figures/` dir before compiling) but should be copied into `icwsm/` properly
  before this is the actual submission tree.
- **Possible prior arXiv preprint** (arxiv.org/abs/2511.03102, same corpus name, earlier
  6-condition snapshot, your name on it) — still unresolved whether this needs citing,
  or affects ICWSM double-blind rules. Your call.

## 3. Remaining steps

1. Decide on the Noto Sans Arabic vs. Amiri question for wherever you actually compile
   for submission (§2).
2. Reformat the 4 `\resizebox` tables to comply with AAAI rules (§2).
3. Confirm the non-Roman-script rule's actual scope for ICWSM (§2) before touching the
   Arabic examples.
4. Copy figures into `icwsm/` properly and fix `\includegraphics` paths for a real
   submission tree (currently only mirrored into a scratch dir for compile-testing).
5. Hash `user_id` in `data/posts/v1/reddit-preprocessed.csv` (and any other
   username-keyed released file) so the stated release policy is true of the actual
   data — operational, not a manuscript-text task (item 7 above).
6. Resolve the arXiv-preprint question (§2).
