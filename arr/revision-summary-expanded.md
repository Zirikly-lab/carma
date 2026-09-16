CARMA — Revision Summary

This cycle addressed six main points: IRB approval, a bias found in LLM-based
filtering, grounding for the group-assignment methodology, a new lexical-semantic
analysis, a substantially expanded and re-validated annotation sample, and the
decision to scope the corpus to Reddit only.

1. IRB Approval
Obtained an exempt IRB approval for this study from our institution (exempt
under DHHS regulatory category 4), covering the collection and release of
publicly available Reddit data containing user self-disclosures of mental
health diagnoses.

2. Excluded LLM Filtering Due to Bias
We evaluated using LLM judges (Qwen2-7B-Instruct, Jais-2-8B-Chat) as an
automatic filter for confirming genuine self-disclosure posts, alongside the
pattern-based extraction pipeline. Comparing the LLM judges against two human
annotators showed the LLMs default to "genuine" far more often than humans do,
recovering only 21-27% of the posts humans flagged as false positives, with
inter-rater agreement dropping from "substantial" (human-human, kappa=0.701) to
"slight-to-fair" (human-LLM, kappa=0.138-0.231). This pattern is consistent with
known LLM leniency/agreeableness bias, dialectal sarcasm blind spots, and
negation-handling weaknesses reported in prior literature. We therefore did not
use LLM votes to filter the released corpus, which is built solely from the
pattern-based extraction pipeline; the LLM comparison is retained in the paper
as a robustness check, not as a filtering mechanism.

3. Grounded Group Assignment in the Self-Reported-Diagnosis Literature
Explicitly grounded the assignment of both diagnosed and control users from
voluntary public self-disclosure (rather than clinical verification) in the
self-reported diagnosis paradigm established by prior computational mental
health research (Coppersmith et al., the CLPsych shared tasks, the SMHD
corpus), and stated the limitations this design inherits from that paradigm:
self-disclosure is a proxy for diagnosis, not a diagnosis itself, so false
negatives (undisclosed diagnoses) and false positives (sarcasm, third-person
mentions) are expected and were quantified through manual annotation.

4. Lexical-Semantic Analysis of the Dataset
Added a log-odds-ratio analysis (with an informative Dirichlet prior, corrected
for single-user artifacts via a minimum-user-support threshold) comparing the
vocabulary of diagnosed vs. control users. This surfaced the terms most
distinctive of each group and revealed that many of the top terms reflect
regional dialect and topic composition rather than condition-specific clinical
language -- a finding we now treat as an important, explicitly-flagged caveat on
the downstream classification results, not just a descriptive statistic.

5. Expanded the Annotation Sample and Improved Agreement
Expanded the manually-annotated validation sample from 100 to 240 posts (20
per retained condition, stratified), with two native Arabic-speaking annotators
labeling each post as a genuine diagnosis disclosure (TP) or a mismatch (FP,
e.g. sarcasm, third-person reference, negation). The larger, more carefully
stratified sample substantially improved measured inter-annotator agreement,
from a lower prior value into the "substantial" agreement band (kappa=0.701,
89.8% raw agreement), giving a more reliable basis for our estimated
false-positive rate (~21.7% of pipeline-confirmed posts).

6. Focused the Corpus on Reddit, Discarding Twitter
Earlier work explored building a parallel Twitter-based corpus alongside the
Reddit data. We discarded the Twitter data, which was noisier and less
suitable for the self-reported-diagnosis paradigm (shorter posts, weaker
longitudinal history, harder self-disclosure matching), and concentrated all
data collection, annotation, and experiments on Reddit, where longer-form,
detailed self-reports and complete retrievable posting histories better
support the corpus's longitudinal design.
