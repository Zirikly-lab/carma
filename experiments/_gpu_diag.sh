#!/bin/bash
#SBATCH --job-name=carma-gpudiag
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v100:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:05:00
#SBATCH --output=logs/gpudiag_%j.out
#SBATCH --error=logs/gpudiag_%j.err

cd /SEAS/home/g21775526/code/carma
echo "Node: $(hostname)"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
echo "--- torch check ---"
/gpfs/automountdir/gpfs/homes/SEAS/home/g21775526/code/carma/.venv-gpu/bin/python -c "
import torch
print('torch:', torch.__version__, 'cuda build:', torch.version.cuda)
print('cuda available:', torch.cuda.is_available())
try:
    x = torch.zeros(1).cuda()
    print('tensor on gpu OK:', x)
except Exception as e:
    print('ERROR:', repr(e))
"
