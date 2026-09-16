# CARMA: ARR → ICWSM Action Plan

Source manuscript: `arr/ARRv3.tex` (ACL format). Reviews: `icwsm/arr-reviews.md` (3 ARR
reviews, all "Resubmit"/"Borderline", none of the numbers in them have changed since —
these reviews are against the *current* ARRv3.tex content, not an older draft).
Target: `icwsm/CARMA.tex` (AAAI format, per `icwsm/aaai-template/`).

## 1. Must-fix content issues (raised by reviewers, still open in ARRv3.tex)

1. **TP/FP/NA inconsistency.** Main text (§3.1) says annotators used a *binary*
   TP/FP scheme. Appendix D (`app:guidelines`, line ~993) says they assigned one of
   **three** labels TP/FP/NA, but the guidelines only define TP and FP — NA is never
   explained, never reported in the confusion matrix (Table 8), and never mentioned in
   the FP-rate computation. All 3 reviewers flag this (R1 explicitly, R2 implicitly).
   **Action:** either (a) confirm NA was never actually assigned and delete it from the
   guidelines text, or (b) add the missing NA definition + report how many posts got NA
   and how they were excluded from the 235-post confusion matrix.
2. **"High precision" framing vs. 21.7% FP rate.** R1 pushes back on calling the
   pipeline "high-precision" while ~1 in 5 pipeline hits are false positives.
   **Action:** soften the "high precision" claims in Abstract/Intro or explicitly
   justify why ~78% precision still counts as high-precision relative to naive keyword
   matching.
3. **"Diagnosed"/"control" terminology.** All 3 reviewers (R1's ethics section too)
   object to "diagnosed users/group" and "control group" as misleading, since neither
   is clinically verified. **Action:** decide on replacement terminology (e.g.
   "self-reported-diagnosis users" / "SR-diagnosed", "screened/non-disclosing users")
   and apply consistently — this is a global find/replace + one clarifying sentence,
   not a new experiment.
4. **LLM classification baseline missing.** R1 asks for Jais/Qwen not just as
   annotator-judges (already in §3.2) but as an actual **classification baseline**
   alongside the classical/PLM models in §5. **Action:** add a zero/few-shot LLM
   classification baseline to Table 3/Appendix B, or explicitly justify its absence.
5. **40-character co-occurrence window is unjustified.** R2 asks for a rationale and
   a sensitivity analysis (why 40 chars, how precision/recall move at other widths).
   **Action:** add a short ablation (e.g. 20/40/80-char windows vs. FP rate) or cite a
   justification if one exists.
6. **Control-group construction may make the task artificially easy.** R2 and R3 both
   want this addressed beyond a caveat — R3 specifically suggests **subreddit-frequency-matched
   control sampling**. Currently only discussed as a Limitations caveat.
   **Action:** either run a matched-control ablation, or make an explicit,
   reviewer-facing case for why that's future work (the Limitations paragraph already
   does the second one — decide if that's enough for ICWSM or needs a real experiment).
7. **Ambiguous release plan.** R3 flags a direct contradiction: Ethical
   Considerations (§Ethics) says "we release only pseudonymized, aggregated statistics
   and model outputs," but Appendix A references a released `reddit-preprocessed.csv`
   file that is post-level. **Action:** pin down and state *one* consistent release
   plan (what's in the DUA-gated release: raw text? user IDs? aggregates only?) and
   make every mention of it agree.
8. **Full post-history / temporal validity.** R2 notes that a post written years
   before disclosure is treated identically to one right after, and some pre-date
   onset entirely. **Action:** at minimum, add a sentence acknowledging this and (if
   feasible) a stat on the distribution of post dates relative to the disclosure post.
9. **Recall inflating F1.** R2 flags some recall scores as "extremely high." **Action:**
   add a sentence in §5/Results interpreting this (likely an artifact of the balanced
   1:1 sampling) — check whether it needs a caveat or a rebalanced-eval ablation.
10. **Dual-use / surveillance risk not discussed.** R3 (Needs Ethics Review: Yes) wants
    explicit discussion of dual-use risk for algorithmic mental-health profiling,
    specifically in the MENA social/legal context — current Ethical Considerations
    section doesn't address this. **Action:** add a paragraph.
11. **Weak PLM baseline (truncation).** R3 notes truncating full history into one
    sequence discards temporal structure. **Action:** at minimum acknowledge as a
    limitation; a windowed/hierarchical PLM baseline would be a stronger fix but is
    optional scope.
12. **Dialect-ID model validation.** R2 asks for more information on how well the
    CAMeLBERT-Mix DID NADI dialect classifier performs (on this domain, not just its
    original benchmark). **Action:** add a sentence citing its reported accuracy, or a
    small spot-check.
13. **Minor/mechanical (do anytime, cheap):**
    - Add a control-group row to Table 2 (corpus summary) — need control post count.
    - "fasttext library" → "FastText library"; "less than 10 words" → "fewer than 10
      words"; "reddit API" → "Reddit API".
    - Use `\url{}` for footnote links so they wrap properly.
    - Double check every table/figure number and caption against current 12-condition
      corpus (old reviewer comments about "12 vs 15 conditions" look stale against the
      current draft, but do one pass to be sure nothing regressed).

## 2. ICWSM/AAAI formatting differences to handle before this compiles/submits

- **Package/preamble swap.** ACL's `acl` package → AAAI's `aaai2026` (`\usepackage[submission]{aaai2026}`), plus the mandated `times/helvet/courier/url/graphicx/natbib/caption` block. Author/affiliation macros differ (`\author{}\affiliations{}` instead of ACL's `\and`-separated block); anonymize as "Anonymous Submission" per the AAAI kit's own instructions.
- **`aaai.bst` naming.** `aaai2026.sty` hardcodes `\bibliographystyle{aaai2026}`, but the template ships the file as `aaai.bst`. Needs a copy/rename to `aaai2026.bst` alongside the manuscript for the bibliography to build.
- **`custom.bib` is missing from the repo entirely** (not tracked, not found anywhere on disk). Nothing will compile past `\bibliography{custom}` until this is located/exported (likely lives in Overleaf) and added under `icwsm/`.
- **`\resizebox` on tables is explicitly disallowed by AAAI** ("must not use resizebox... to make it smaller"). ARRv3.tex uses it on 4 tables (full classical/PLM results, the two phrase-inventory tables). These will need reformatting (split tables, `\tabcolsep`, shortened headers) — flagged, not yet done.
- **Non-Roman script restriction.** AAAI's camera-ready rule says Arabic/other non-Latin text "must be restricted to bit-mapped figures" — but the paper's entire method (keyword/phrase tables, worked examples) depends on inline Arabic via `babel`+`Noto Sans Arabic`. **This needs to be verified against the actual current ICWSM author kit / CFP**, not assumed from this generic 2026 AAAI Press kit — sociolinguistic/dialect papers at ICWSM commonly keep inline non-English text, so the restriction may not apply as written, or may only bind at camera-ready. Don't spend effort converting Arabic to images until this is confirmed.
- **Section numbering vs. `\S\ref{...}` cross-references.** AAAI template defaults to `\setcounter{secnumdepth}{0}` (no section numbers), but ARRv3.tex leans on `\S\ref{sec:...}` throughout for cross-references, which needs numbered sections to render correctly. Set `secnumdepth` to 2 in the ported file (done below).
- **Single-file submission rule.** AAAI wants one `.tex` file (no `\input`) — not an issue, ARRv3.tex is already a single file.
- **No hyperref, no page numbers, no `\vspace{-...}`, no float resizing** — sweep for these once content is finalized; none currently used except the resizebox tables above.
- **Figures.** ARRv3.tex references `latex/figures/fig_*.png`; actual files live at `data/posts/v1/fig_*.png`. Need to copy/relocate figures into `icwsm/` and fix paths once we're past the "content as-is" copy step.

## 3. Immediate next steps

1. [Done] Copy ARRv3.tex content into `icwsm/CARMA.tex` inside the AAAI template shell,
   as-is, so the content lives in the right place before revising it.
2. [Done] Append the official AAAI/ICWSM Paper Checklist (`arr/paper-checklist.tex`) as
   the final appendix section (`Appendix H, \label{app:checklist}`), per that file's own
   instructions (Overview/Detailed-Instructions text and subsection headers dropped,
   only the enumerated Checklist kept). All answers are still `\answerTODO{Answer}`
   placeholders — filling these in honestly (with section references) is a required
   step before submission, not just formatting. Two checklist items cite `\citet{fair}`
   and `\citet{gebru2021datasheets}`, which need entries added to `custom.bib`.
3. Locate `custom.bib` (or re-export from Overleaf) and drop it in `icwsm/`.
4. Copy figure PNGs from `data/posts/v1/` into `icwsm/figures/` and fix `\includegraphics` paths.
5. Work through §1 review items above, roughly in order of effort: terminology (3) and
   mechanical fixes (13) first, then the missing-NA/release-plan inconsistencies (1, 7),
   then the substantive additions (4, 5, 6, 10) that need new analysis/experiments.
6. Once content is stable, do the AAAI-compliance pass from §2 (resizebox tables, Arabic-script rule check, page-limit check against the actual ICWSM CFP).
7. Fill in the Paper Checklist (step 2) honestly against the finished manuscript.
