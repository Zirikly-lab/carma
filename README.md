
This repo hosts code for old carma pipeline (in the legacy folder) and the new version, v2. We fix ARR feedback in this repo including annotation and classification pipelines rerunning.

# Data

## LLM as judge
* Annotate using qwen for x dataset. We skipped this.
* Rerun annotation for jais for better parse error 

## Featch all twitter profiles AGAIN
We are building a new version of the dataset based on majority vote instead of unanimity. The problem with this is there is a lot more users in the majority vote version than unanimous. We need to download the complete post history of those users using the slow, tedious twitter scrapper Amal built.


## Manual annotation
We need to annotate a bigger sample, miniorty class aware. We sampe 50 posts from each condition for the top conditions. This results in:
* 650 posts for twitter
* 700 posts for reddit

Yes, we will be annotating a lot. We need to all work on this, in addittion to seeking outside help. If you know any arabic speakers please reach out to Saad.
