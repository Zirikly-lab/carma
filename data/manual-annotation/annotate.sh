#!/bin/bash
#SBATCH --job-name=carma-annotate
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=logs/annotate_%j.out
#SBATCH --error=logs/annotate_%j.err

set -e

cd /SEAS/home/g21775526/code/carma
source /SEAS/home/g21775526/code/venv/bin/activate

mkdir -p logs

echo "Node: $(hostname)"
echo "GPUs: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"

# Fix torch: upgrade from cu130 (needs nonexistent CUDA 13.0 driver) to cu126 (works on CUDA 12.9)
echo "Fixing torch CUDA version..."
pip install --quiet \
    "torch==2.11.0+cu126" \
    "torchvision==0.26.0+cu126" \
    --index-url https://download.pytorch.org/whl/cu126

# 4-bit quantization via bitsandbytes
pip install --quiet bitsandbytes

python -c "import torch; print('torch:', torch.__version__, '| CUDA available:', torch.cuda.is_available())"

# Qwen2-7B-Instruct in 4-bit: ~3.5GB VRAM — well within V100 16GB
# batch-size 1: avoids padding-driven OOM (prior batch-size 8 OOM'd both batches)
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
python manual_annotation.py \
    --model Qwen/Qwen2-7B-Instruct \
    --backend transformers \
    --load-in-4bit \
    --batch-size 1
