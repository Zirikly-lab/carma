#!/usr/bin/env python3
"""
Manual annotation for CARMA Reddit sample using Qwen2-72B via vLLM.

Input:  data/manual-annotation/reddit-sample-qwen.csv
Output: same file with an added 'annotation' column (TP | FP | NA).

Labels (from data/manual-annotation/guidelines.txt):
  TP  – You believe this person has the condition (no official dx required;
         symptoms, meds, or sincere self-report are enough).
  FP  – Clear algorithmic error: sarcasm, third-person, figurative use, etc.
         NOT for weak/uncertain cases — those go to NA.
  NA  – Algorithm matched but you cannot confidently decide TP or FP.
         Use as a last resort; try TP or FP first.
"""

import re
import sys
import argparse
import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm
from transformers import AutoTokenizer

# ---------------------------------------------------------------------------
# Configuration (overridable via CLI)
# ---------------------------------------------------------------------------
MODEL_NAME      = "Qwen/Qwen2-72B"
INPUT_PATH      = "data/manual-annotation/reddit-sample-qwen.csv"
OUTPUT_PATH     = "data/manual-annotation/reddit-sample-qwen.csv"
ANNOTATION_COL  = "annotation"
MAX_NEW_TOKENS  = 50    # enough for label even if model prefaces it with a word or two
BATCH_SIZE      = 32
CHECKPOINT_EVERY = 10   # save every N batches
TENSOR_PARALLEL  = 4

CONDITION_AR = {
    "adhd":            "فرط الحركة وتشتت الانتباه",
    "anxiety":         "اضطراب القلق",
    "autism":          "التوحد",
    "bipolar":         "ثنائي القطب",
    "bpd":             "اضطراب الشخصية الحدية",
    "depression":      "الاكتئاب",
    "eating_disorder": "اضطراب الأكل",
    "ocd":             "الوسواس القهري",
    "panic":           "اضطراب الهلع",
    "ptsd":            "اضطراب ما بعد الصدمة",
    "schizophrenia":   "الفصام",
    "sleep_disorder":  "اضطراب النوم",
    "suicidal":        "الأفكار الانتحارية",
}

# ---------------------------------------------------------------------------
# Prompt (reflects the annotation guidelines)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are an Arabic mental health annotation specialist. \
Classify each Reddit post with exactly one label: TP, FP, or NA.

TP (True Positive): author genuinely has the condition — sincerely says so, describes symptoms, mentions meds/treatment, or seeks help for themselves.
FP (False Positive): clear mismatch — sarcasm/humor, talking about someone else, figurative use, negation, news/awareness content, professional account.
NA (Need more info): ambiguous — too vague, uncertain language ("حاسس", "ممكن"), cannot confidently decide TP or FP. Use sparingly.\
"""

# Few-shot examples shown in the user turn to force label-only output
FEW_SHOT = """\
Examples:
Post: انا عندي اكتئاب
Condition: depression (الاكتئاب)
Label: TP

Post: اخويا عنده اكتئاب
Condition: depression (الاكتئاب)
Label: FP

Post: الاكتئاب هيموتني ههههههه
Condition: depression (الاكتئاب)
Label: FP

Post: حاسس عندي اكتئاب
Condition: depression (الاكتئاب)
Label: NA

Now classify:
Post: {post}
Condition: {condition} ({condition_ar})
Label:\
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_condition_ar(diagnosis: str) -> str:
    return CONDITION_AR.get(str(diagnosis).lower().strip(), "")


def build_prompt(row: pd.Series, tokenizer) -> str:
    condition    = str(row.get("diagnosis", ""))
    condition_ar = get_condition_ar(condition)
    post         = str(row.get("text", ""))

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": FEW_SHOT.format(
                post=post,
                condition=condition,
                condition_ar=condition_ar,
            ),
        },
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def parse_label(raw_text: str) -> str:
    """Extract TP / FP / NA from model output; return PARSE_FAIL otherwise."""
    if not raw_text or not raw_text.strip():
        return "PARSE_FAIL"
    # Direct label match first
    m = re.search(r"\b(TP|FP|NA)\b", raw_text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    # Verbose fallback: catch spelled-out forms
    t = raw_text.lower()
    if "true positive" in t:
        return "TP"
    if "false positive" in t:
        return "FP"
    if "need more" in t or "not applicable" in t or "not enough" in t:
        return "NA"
    return "PARSE_FAIL"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run_vllm(todo_indices, df, model_name, tp_size, batch_size):
    from vllm import LLM, SamplingParams
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, use_fast=False)
    llm = LLM(
        model=model_name,
        tensor_parallel_size=tp_size,
        max_model_len=4096,
        trust_remote_code=True,
        dtype="bfloat16",
        gpu_memory_utilization=0.9,
    )
    sampling_params = SamplingParams(max_tokens=MAX_NEW_TOKENS, temperature=0, top_p=1)

    def generate_batch(batch_idx):
        prompts = [build_prompt(df.loc[i], tokenizer) for i in batch_idx]
        outputs = llm.generate(prompts, sampling_params)
        return [out.outputs[0].text for out in outputs]

    return tokenizer, generate_batch


def run_transformers(todo_indices, df, model_name, batch_size, load_in_4bit=False):
    import torch
    # Import only what we need — avoids the torchvision import that pipeline triggers
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, use_fast=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    load_kwargs = dict(device_map="auto", trust_remote_code=True)
    if load_in_4bit:
        print(f"Loading model in 4-bit (BnB) …")
        load_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
    else:
        print(f"Loading model in bfloat16 …")
        load_kwargs["torch_dtype"] = torch.bfloat16

    model = AutoModelForCausalLM.from_pretrained(model_name, **load_kwargs)
    model.eval()

    def generate_batch(batch_idx):
        prompts = [build_prompt(df.loc[i], tokenizer) for i in batch_idx]
        inputs = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=4096,
        ).to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        out_texts = []
        for i, ids in enumerate(output_ids):
            # Decode only the newly generated tokens
            new_tokens = ids[inputs["input_ids"].shape[1]:]
            out_texts.append(tokenizer.decode(new_tokens, skip_special_tokens=True))
        return out_texts

    return tokenizer, generate_batch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL_NAME)
    parser.add_argument("--backend", choices=["vllm", "transformers"], default="vllm")
    parser.add_argument("--tensor-parallel-size", type=int, default=TENSOR_PARALLEL)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--limit", type=int, default=None, help="Process only first N unannotated rows (for testing)")
    parser.add_argument("--load-in-4bit", action="store_true", help="Load model in 4-bit (bitsandbytes NF4) to save VRAM")
    args = parser.parse_args()

    model_name   = args.model
    tp_size      = args.tensor_parallel_size
    batch_size   = args.batch_size

    print(f"Loading {INPUT_PATH} …")
    # keep_default_na=False prevents pandas from parsing "NA" labels as NaN
    df = pd.read_csv(INPUT_PATH, keep_default_na=False)

    if ANNOTATION_COL not in df.columns:
        df[ANNOTATION_COL] = pd.NA

    # Resume: skip rows that already have a valid label
    valid = {"TP", "FP", "NA"}
    todo_mask    = ~df[ANNOTATION_COL].isin(valid)
    todo_indices = df[todo_mask].index.tolist()
    n_done       = len(df) - len(todo_indices)

    if args.limit:
        todo_indices = todo_indices[: args.limit]

    print(f"{len(todo_indices)} rows to annotate  ({n_done} already done, {len(df)} total)")

    if not todo_indices:
        print("Nothing to do.")
        return

    print(f"Initializing {args.backend} backend ({model_name}) …")
    if args.backend == "vllm":
        _, generate_batch = run_vllm(todo_indices, df, model_name, tp_size, batch_size)
    else:
        _, generate_batch = run_transformers(todo_indices, df, model_name, batch_size, load_in_4bit=args.load_in_4bit)

    parse_fail_count = 0

    for batch_start in tqdm(range(0, len(todo_indices), batch_size), desc="Annotating"):
        batch_idx = todo_indices[batch_start : batch_start + batch_size]

        try:
            texts = generate_batch(batch_idx)
            for row_idx, text in zip(batch_idx, texts):
                label = parse_label(text)
                df.at[row_idx, ANNOTATION_COL] = label
                if label == "PARSE_FAIL":
                    parse_fail_count += 1
        except Exception as exc:
            print(f"\nBatch error: {exc}", file=sys.stderr)
            for row_idx in batch_idx:
                df.at[row_idx, ANNOTATION_COL] = "PARSE_FAIL"
            parse_fail_count += len(batch_idx)

        batch_num = batch_start // batch_size + 1
        if batch_num % CHECKPOINT_EVERY == 0:
            df.to_csv(OUTPUT_PATH, index=False)
            done_so_far = batch_start + len(batch_idx)
            print(f"  checkpoint saved ({done_so_far}/{len(todo_indices)} annotated)")

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved to {OUTPUT_PATH}")
    print("\nLabel distribution:")
    print(df[ANNOTATION_COL].value_counts())
    if parse_fail_count:
        print(f"\nWarning: {parse_fail_count} PARSE_FAIL rows — re-run to retry.")


if __name__ == "__main__":
    main()
