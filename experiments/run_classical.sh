#!/bin/bash
#SBATCH --job-name=carma-classical
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/classical_%j.out
#SBATCH --error=logs/classical_%j.err

set -e

cd /SEAS/home/g21775526/code/carma
source /SEAS/home/g21775526/code/venv/bin/activate

mkdir -p logs results

echo "Node: $(hostname)"
echo "CPUs: $(nproc)"

pip install --quiet xgboost scikit-learn pandas

python experiments/classical.py --output results/classical.csv
