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

python experiments/classical.py "${LEVEL_FLAG[@]}" --output "results/classical_${LEVEL}.csv"
