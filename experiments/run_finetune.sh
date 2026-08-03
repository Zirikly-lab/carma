#!/bin/bash
#SBATCH --job-name=carma-finetune
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v100:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=12:00:00
#SBATCH --output=logs/finetune_%j.out
#SBATCH --error=logs/finetune_%j.err

set -e

cd /SEAS/home/g21775526/code/carma
export PYTHONNOUSERSITE=1
PYTHON=/gpfs/automountdir/gpfs/homes/SEAS/home/g21775526/code/carma/.venv/bin/python

mkdir -p logs results

echo "Node: $(hostname)"
echo "GPUs: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"

# MODEL is passed as --export MODEL=arabert or camelbert
MODEL=${MODEL:-arabert}
echo "Fine-tuning model: $MODEL"

# USER_LEVEL is passed as --export USER_LEVEL=1 to aggregate posts per user
# instead of the default post-level examples
USER_LEVEL=${USER_LEVEL:-0}
LEVEL_FLAG=()
LEVEL=post
if [ "$USER_LEVEL" = "1" ]; then
    LEVEL_FLAG=(--user-level)
    LEVEL=user
fi
echo "Level: $LEVEL"

$PYTHON experiments/finetune.py \
    --model "$MODEL" \
    --condition all \
    "${LEVEL_FLAG[@]}" \
    --output "results/finetune_${MODEL}_${LEVEL}.csv"
