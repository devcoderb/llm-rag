#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# kubeflow/setup_env.sh  (Assignment 2B: RAG pipeline)
#
# Creates a lean Python venv on the persistent Kubeflow volume and registers it
# as the Jupyter kernel "Python (RAG venv)". The 1A venv (./venv) is NOT touched.
#
# RUN (from any directory; defaults to the Group 157 volume):
#   bash kubeflow/setup_env.sh
#   VOLUME_ROOT=/home/other bash kubeflow/setup_env.sh      # different volume
#
# WHAT IT DOES
#   - Creates $VOLUME_ROOT/venv-rag with --system-site-packages, so it inherits the
#     image's working torch + CUDA (no ~3 GB GPU wheel download).
#   - Installs ONLY what the RAG notebook needs, from kubeflow/requirements.txt (the same file
#     check_env.py verifies against, so the two cannot drift). Same pins as 1A plus rank_bm25.
#     Dropped versus 1A (not used by 2B): trl, datasets, evaluate, wandb, matplotlib, seaborn,
#     sentencepiece, protobuf.
#   - Registers the kernel and saves the exact versions next to the venv.
#
# Idempotent: later runs are fast and mainly re-register the kernel (the venv
# persists across pod restarts, the kernel registration does not).
# ---------------------------------------------------------------------------
# Re-launch in bash if started with sh/dash (pipefail and BASH_SOURCE need bash).
if [ -z "${BASH_VERSION:-}" ]; then
    exec bash "$0" "$@"
fi
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VOLUME_ROOT="${VOLUME_ROOT:-/home/group157}"
VENV_DIR="${VENV_DIR:-$VOLUME_ROOT/venv-rag}"
KERNEL_NAME="rag-venv"
KERNEL_DISPLAY="Python (RAG venv)"

echo "==========================================="
echo " Assignment 2B environment setup"
echo " Volume root : $VOLUME_ROOT"
echo " Venv        : $VENV_DIR"
echo " Started     : $(date)"
echo "==========================================="

echo ""
echo "--- [1/5] Checks ---"
if [ ! -d "$VOLUME_ROOT" ] || [ ! -w "$VOLUME_ROOT" ]; then
    echo "ERROR: $VOLUME_ROOT does not exist or is not writable. Set VOLUME_ROOT to your persistent volume." >&2
    exit 1
fi
echo "Free space on volume: $(df -h "$VOLUME_ROOT" | awk 'NR==2{print $4}')"
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader || echo "nvidia-smi failed (GPU may be busy)"
else
    echo "NOTE: no GPU visible. Stages 0 to 5 run on CPU; the generator and judge (Stages 6 and 7) need a GPU."
fi
if command -v python3.11 >/dev/null 2>&1; then PYBIN="python3.11"; else PYBIN="python3"; fi
echo "Interpreter: $($PYBIN --version 2>&1)"

echo ""
echo "--- [2/5] Virtual environment ---"
if [ -d "$VENV_DIR" ]; then
    echo "venv already exists (reusing it)."
else
    $PYBIN -m venv --system-site-packages "$VENV_DIR"
    echo "Created $VENV_DIR"
fi
PIP="$VENV_DIR/bin/pip"
PY="$VENV_DIR/bin/python"
"$PY" - <<'PYCHECK'
try:
    import torch
    print(f"Inherited torch {torch.__version__}, CUDA available: {torch.cuda.is_available()}")
except Exception as e:
    print(f"NOTE: torch not visible in the venv yet ({e}).")
PYCHECK

echo ""
echo "--- [3/5] Installing packages (2-4 minutes the first time) ---"
"$PIP" install --upgrade pip --quiet
"$PIP" install --quiet -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "--- [4/5] Registering Jupyter kernel ---"
"$PY" -m ipykernel install --user --name "$KERNEL_NAME" --display-name "$KERNEL_DISPLAY"

echo ""
echo "--- [5/5] Freezing versions ---"
"$PIP" freeze > "$VOLUME_ROOT/rag_requirements.txt"
echo "Saved: $VOLUME_ROOT/rag_requirements.txt"

echo ""
echo "==========================================="
echo " Setup complete"
echo "==========================================="
echo "NEXT STEPS"
echo "  1. Verify (optional): $PY $SCRIPT_DIR/check_env.py"
echo "  2. In the notebook: Kernel -> Change Kernel -> \"$KERNEL_DISPLAY\""
echo "If the kernel is missing after a pod restart, just re-run: bash $SCRIPT_DIR/setup_env.sh"
