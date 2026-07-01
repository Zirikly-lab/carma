#!/bin/bash
#SBATCH --job-name=carma-setup
#SBATCH --partition=superChip
#SBATCH --gres=gpu:gh200:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=logs/setup_gh200_%j.out
#SBATCH --error=logs/setup_gh200_%j.err

export PYTHONNOUSERSITE=1
echo "Node: $(hostname) | Arch: $(uname -m)"
echo "=== Checking for nvshmem ==="
find /usr /opt /c1 -name "libnvshmem*" 2>/dev/null | head -10 || true

echo "=== Available module paths ==="
module avail 2>&1 | grep -iE "nvshmem|nccl|cuda" | head -15 || true

echo "=== Creating new conda env ==="
MAMBA=/SEAS/home/g21775526/miniforge3/bin/mamba
if [ ! -f "$MAMBA" ]; then
    MAMBA=/SEAS/home/g21775526/miniforge3/bin/conda
fi

$MAMBA create -y -p /SEAS/home/g21775526/miniforge3/envs/carma-gh200 \
    python=3.11 \
    -c defaults -c conda-forge
if [ $? -ne 0 ]; then echo "FATAL: env creation failed"; exit 1; fi

ENVPY=/SEAS/home/g21775526/miniforge3/envs/carma-gh200/bin/python

echo "=== Installing PyTorch (cu128 aarch64) ==="
$ENVPY -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
if [ $? -ne 0 ]; then echo "FATAL: torch install failed"; exit 1; fi

echo "=== Installing other deps ==="
$ENVPY -m pip install transformers scikit-learn pandas numpy
if [ $? -ne 0 ]; then echo "FATAL: deps install failed"; exit 1; fi

echo "=== Verifying ==="
PYTHONNOUSERSITE=1 $ENVPY -c "
import torch, transformers, sklearn, pandas
print('torch:', torch.__version__, '| cuda:', torch.cuda.is_available())
print('transformers:', transformers.__version__)
print('sklearn:', sklearn.__version__)
print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none')
"
if [ $? -ne 0 ]; then echo "FATAL: verification failed"; exit 1; fi
echo "=== Setup complete. Env at /SEAS/home/g21775526/miniforge3/envs/carma-gh200 ==="
