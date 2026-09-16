Paper Summary:

The paper introduced CARMA, an Arabic mental health corpus, collected from reddit, containing 12 conditions along with a neutral/control groups set. The dataset is mainly collected using a pattern-based framework which relies on self-disclosure of mental health with some human validation.
Summary Of Strengths:

The work is interesting and will be a significant resource for the community. The data extraction pipeline is dialect-aware and relies on self-disclosure however the posts with direct content on the condition are removed to stop information leakage during experiments.
Summary Of Weaknesses:

The paper still has significant concerns.

The annotation protocol is not clear. The main text uses a binary TP/FP scheme, while the appendix introduces TP/FP/NA. The authors should clarify how NA cases were handled and how the false-positive rate was computed. They should also justify describing the framework as high precision when the human-estimated FP rate is about 21.7%.

I would also urge the authors to reconsider the terms diagnosed group and control group, these terms are misleading. The positive group is based on self-disclosure rather than clinical diagnosis, while the control group may still include users with undetected conditions.

LLM results from Jais and Qwen should be included in the main paper, as the disagreement with human annotators is informative, also if possible as a baseline model performance as this will give us an idea of the current model's performance on such cases for mid/low-resource language.
Comments Suggestions And Typos:

Annotation protocol: The main content says the human annotated binary labels whereas in the appendix it is written as a 3-class (TP, FP, and NA) problem. Please elaborate and make it consistent (see weakness comment)

Please fix Tab5 Please check Tab7, the caption says 12 but all the 15 conditions are present. Fig 1 Egypt % does not match the text so revise
Confidence: 4 = Quite sure. I tried to check the important points carefully. It's unlikely, though conceivable, that I missed something that should affect my ratings.
Soundness: 2 = Poor: Some of the main claims are not sufficiently supported. There are major technical/methodological problems.
Excitement: 2.5
Overall Assessment: 2.5 = Borderline Findings
Ethical Concerns:

In addition to the sensative nature of the data, I am also concerned about the terminilogy used here :“diagnosed users” and “control users” which is potentially misleading. There is no clinical verification that the positive users have been formally diagnosed, and the control users may still have a mental health condition that was simply not detected through the proposed pipeline. So my suggestion would be rephrase to more lighter terminology.
Needs Ethics Review: Yes
Reproducibility: 2 = They would be hard pressed to reproduce the results: The contribution depends on data that are simply not available outside the author's institution or consortium and/or not enough details are provided.
Datasets: 3 = Potentially useful: Someone might find the new datasets useful for their work.
Software: 1 = No usable software released.
Knowledge Of Or Educated Guess At Author Identity: No
Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
Knowledge Of Paper Source: N/A, I do not know anything about the paper from outside sources
Impact Of Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
Reviewer Certification: I certify that the review I entered accurately reflects my assessment of the work. If you used any type of automated tool to help you craft your review, I hereby certify that its use was restricted to improving grammar and style, and the substance of the review is either my own work or the work of an acknowledged secondary reviewer.
Publication Ethics Policy Compliance: I did not use any generative AI tools for this review
Add:
Official Review of Submission2770 by Reviewer Kqw9
Official Reviewby Reviewer Kqw909 Sept 2026, 18:06 (modified: 15 Sept 2026, 10:29)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Ethics Reviewers, Ethics Chairs, Reviewer Kqw9, AuthorsRevisions
Paper Summary:

This paper introduces CARMA, a large Arabic Reddit corpus for computational mental-health research, covering 12 mental disorder categories and a control group. The focus on Arabic dialects makes the work potentially useful for future research. The authors provide baseline results for the classification of mental disorders, accompanied by an analysis of the most frequent words in the positive and negative samples.
Summary Of Strengths:

    The paper addresses an important gap by collecting a large-scale Arabic resource for NLP mental health
    The corpus has broad condition coverage, spanning 12 target categories.
    I appreciate the effort to account for Arabic dialectal variation during dataset construction

Summary Of Weaknesses:

    Please refrain from using diagnosed users/conditions if the diagnoses were not verified and are only self-mentions from Reddit users.
    The choice of a 40-character co-occurrence window needs justification and a sensitivity analysis. Why has this threshold been used? It seems quite permissive and may introduce more false positives.
    The control group construction is too restrictive regarding the discussion of mental health related topics and may itself make the classification task artificially easy.
    The estimated false positive rate is pretty high at around 20%. Have you thought about validating more or even all the data? In addition, have the incorrectly labeled users been removed from the dataset?
    I have some concerns related to the choice of collecting all the post history of a user. Consequently, a post written years before the disclosure is treated identically to one written immediately after it. In addition, some posts may even precede the actual onset or diagnosis.
    Some recall scores are extremely high, inflating the F1 scores reported in the main body of the paper.

Comments Suggestions And Typos:

Could you also add the control group information to Table 2?

Could you please provide more information on the performance of the model used for dialect identification?
Confidence: 5 = Positive that my evaluation is correct. I read the paper very carefully and am familiar with related work.
Soundness: 3 = Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details.
Excitement: 4 = Exciting: I would mention this paper to others and/or make an effort to attend its presentation in a conference.
Overall Assessment: 2 = Resubmit next cycle: I think this paper needs substantial revisions that can be completed by the next ARR cycle.
Ethical Concerns:

There are no concerns with this submission
Needs Ethics Review: No
Reproducibility: 3 = They could reproduce the results with some difficulty. The settings of parameters are underspecified or subjectively determined, and/or the training/evaluation data are not widely available.
Datasets: 3 = Potentially useful: Someone might find the new datasets useful for their work.
Software: 1 = No usable software released.
Knowledge Of Or Educated Guess At Author Identity: No
Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
Knowledge Of Paper Source: N/A, I do not know anything about the paper from outside sources
Impact Of Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
Reviewer Certification: I certify that the review I entered accurately reflects my assessment of the work. If you used any type of automated tool to help you craft your review, I hereby certify that its use was restricted to improving grammar and style, and the substance of the review is either my own work or the work of an acknowledged secondary reviewer.
Publication Ethics Policy Compliance: I used a privacy-preserving tool exclusively for the use case(s) approved by PEC policy, such as language edits
Add:
Official Review of Submission2770 by Reviewer ziAk
Official Reviewby Reviewer ziAk08 Sept 2026, 03:59 (modified: 15 Sept 2026, 10:29)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Ethics Reviewers, Ethics Chairs, Reviewer ziAk, AuthorsRevisions
Paper Summary:

The authors introduce CARMA, a large-scale Arabic dataset constructed from Reddit to support mental health analysis. Utilizing a pattern-based, dialect-aware self-reported diagnosis extraction pipeline, the authors identify 4,365 diagnosed users (spanning 12 mental health conditions) and 2,875 control users, totaling ~625K posts. The paper validates the extraction pipeline via human annotation, conducts a linguistic analysis using log-odds ratios, and establishes benchmark performances using classical classifiers and pre-trained language models (PLMs).
Summary Of Strengths:

    Crucial Resource: Introduces a much-needed, large-scale, multi-condition dataset for Arabic mental health NLP.
    Robust Extraction Pipeline: The dialect-aware pipeline is meticulously designed, accounting for regional phrasing and orthographic variations (well-documented in the appendices).
    Scientific Transparency: The authors explicitly analyze and document the dialectal/topical skews in the dataset, correctly acknowledging that the baselines reflect dataset separability as much as clinical signal.

Summary Of Weaknesses:

    Severe Ethical Gaps: The paper fails to discuss the dual-use risks of algorithmic mental health surveillance, particularly given the social and legal context of mental health in the MENA region.
    Ambiguous Release Plan: The authors contradict themselves regarding whether they are releasing text, user IDs, or just aggregated statistics (Lines 702-708).
    Control Group Sampling: Models are heavily confounded by dialectal and topical shifts between the control and diagnosed groups. A matched-control sampling strategy (matching by subreddit frequency) is needed to prove actual clinical separability.
    Weak PLM Baseline: Truncating a user's entire history into a single sequence for PLM evaluation discards the temporal nature of the data.

Comments Suggestions And Typos:

    Line 240: "fasttext library" -> Capitalize as "FastText library".
    Line 244: "with less than 10 words" -> "with fewer than 10 words".
    Line 245: "reddit API" -> Capitalize as "Reddit API". Footnotes 1 and 6: The URLs break somewhat awkwardly across lines. Ensure you are using the \url{} package to handle line breaks in hyperlinks properly.

Confidence: 4 = Quite sure. I tried to check the important points carefully. It's unlikely, though conceivable, that I missed something that should affect my ratings.
Soundness: 3 = Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details.
Excitement: 3 = Interesting: I might mention some points of this paper to others and/or attend its presentation in a conference if there's time.
Overall Assessment: 2 = Resubmit next cycle: I think this paper needs substantial revisions that can be completed by the next ARR cycle.
Limitations And Societal Impact:

The confusing language regarding the data release mechanism must also be resolved.
Ethical Concerns:

Methodologically and technically, this is a highly valuable resource for Arabic NLP. However, the ethical considerations are currently treated as a checklist rather than a serious engagement with the risks of building psychiatric profiling tools for vulnerable populations.
Needs Ethics Review: Yes
Reproducibility: 3 = They could reproduce the results with some difficulty. The settings of parameters are underspecified or subjectively determined, and/or the training/evaluation data are not widely available.
Datasets: 2 = Documentary: The new datasets will be useful to study or replicate the reported research, although for other purposes they may have limited interest or limited usability. (Still a positive rating)
Software: 1 = No usable software released.
Knowledge Of Or Educated Guess At Author Identity: No
Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
Knowledge Of Paper Source: N/A, I do not know anything about the paper from outside sources
Impact Of Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
Reviewer Certification: I certify that the review I entered accurately reflects my assessment of the work. If you used any type of automated tool to help you craft your review, I hereby certify that its use was restricted to improving grammar and style, and the substance of the review is either my own work or the work of an acknowledged secondary reviewer.
Publication Ethics Policy Compliance: I did not use any generative AI tools for this review