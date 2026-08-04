#!/bin/bash
#SBATCH --job-name=carma-jais
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

# Fix torch CUDA version
echo "Fixing torch CUDA version..."
pip install --quiet \
    "torch==2.11.0+cu126" \
    "torchvision==0.26.0+cu126" \
    --index-url https://download.pytorch.org/whl/cu126

pip install --quiet bitsandbytes

python -c "import torch; print('torch:', torch.__version__, '| CUDA available:', torch.cuda.is_available())"

# Jais-2-8B-Chat in 4-bit: ~4GB VRAM, well within V100 16GB
# batch-size 1: avoids padding-driven OOM
# Reads from fady CSV (base data), writes to dedicated jais CSV
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
python data/manual-annotation/manual_annotation.py \
    --model inceptionai/Jais-2-8B-Chat \
    --input  data/manual-annotation/reddit-sample-fady.csv \
    --output data/manual-annotation/reddit-sample-jais.csv \
    --backend transformers \
    --load-in-4bit \
    --batch-size 1
