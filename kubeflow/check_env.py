#!/usr/bin/env python
"""
kubeflow/check_env.py  (Assignment 2B)

Verifies the RAG environment created by kubeflow/setup_env.sh. The expected versions are read from
kubeflow/requirements.txt, the same file setup_env.sh installs from, so the two cannot drift apart.

    python llm-rag/kubeflow/check_env.py        (re-launches itself with the venv's python if needed)

GPU checks are informational: Stages 0 to 5 run on CPU, only Stages 6 and 7 need a GPU.
Exits 0 when every required check passes, 1 otherwise.
Optional environment variables: CHECK_REQUIREMENTS (path to another requirements file),
VENV_DIR (expected venv path; default $VOLUME_ROOT/venv-rag with VOLUME_ROOT=/home/group157).
"""
import importlib
import importlib.metadata as md
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REQ_FILE = Path(os.environ.get("CHECK_REQUIREMENTS", HERE / "requirements.txt"))
VENV_DIR = Path(os.environ.get("VENV_DIR", Path(os.environ.get("VOLUME_ROOT", "/home/group157")) / "venv-rag"))

# pip distribution name -> importable module name (everything else: replace '-' with '_')
MODULE_NAMES = {"scikit-learn": "sklearn", "faiss-cpu": "faiss", "sentence-transformers": "sentence_transformers"}


def line(n=60):
    print("-" * n)


def read_requirements(path):
    from packaging.requirements import Requirement
    reqs = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        text = raw.split("#", 1)[0].strip()
        if text:
            reqs.append(Requirement(text))
    return reqs


def check_interpreter():
    print("\n--- Interpreter ---")
    line()
    print(f"  python executable : {sys.executable}")
    print(f"  expected venv     : {VENV_DIR}")
    inside = Path(sys.prefix).resolve() == VENV_DIR.resolve() if VENV_DIR.exists() else False
    print("  OK: running inside the RAG venv." if inside else
          "  WARNING: not the RAG venv interpreter (select the 'Python (RAG venv)' kernel in the notebook).")
    return True   # warning only


def check_packages():
    print(f"\n--- Packages from {REQ_FILE.name} ---")
    line()
    ok = True
    try:
        reqs = read_requirements(REQ_FILE)
    except Exception as e:
        print(f"  cannot read requirements: {e}")
        return False
    for req in reqs:
        module = MODULE_NAMES.get(req.name, req.name.replace("-", "_"))
        try:
            installed = md.version(req.name)
        except md.PackageNotFoundError:
            print(f"  {req.name:<26}MISSING")
            ok = False
            continue
        spec_ok = req.specifier.contains(installed, prereleases=True) if str(req.specifier) else True
        try:
            importlib.import_module(module)
            import_ok = True
        except Exception as e:
            import_ok = False
            err = f" import failed: {e}"
        status = "OK" if spec_ok and import_ok else ("MISMATCH (wanted " + str(req.specifier) + ")" if not spec_ok else err)
        print(f"  {req.name:<26}{installed:<14}{status}")
        ok &= spec_ok and import_ok
    # torch comes from the Kubeflow image
    try:
        import torch
        torch_ok = torch.__version__.startswith("2.")
        print(f"  {'torch (image)':<26}{torch.__version__:<14}{'OK' if torch_ok else 'MISMATCH (wanted 2.x)'}")
        ok &= torch_ok
    except Exception as e:
        print(f"  torch (image)             MISSING ({e})")
        ok = False
    return ok


def check_functional():
    print("\n--- Functional smoke tests (no model downloads) ---")
    line()
    ok = True
    try:
        import faiss
        import numpy as np
        index = faiss.IndexFlatIP(4)
        index.add(np.eye(4, dtype="float32"))
        _, ids = index.search(np.eye(4, dtype="float32")[:1], 1)
        assert int(ids[0][0]) == 0
        print("  faiss IndexFlatIP add/search OK")
    except Exception as e:
        ok = False
        print(f"  faiss FAILED: {e}")
    try:
        from rank_bm25 import BM25Okapi
        # 3 documents: with only 2, BM25Okapi gives a term in one document an IDF of 0
        bm = BM25Okapi([["rbi", "master", "direction"], ["sebi", "buyback", "regulations"], ["upi", "payments", "vision"]])
        scores = bm.get_scores(["sebi"])
        assert scores[1] > scores[0] and scores[1] > scores[2]
        print("  rank_bm25 scoring OK")
    except Exception as e:
        ok = False
        print(f"  rank_bm25 FAILED: {e}")
    try:
        from sentence_transformers import CrossEncoder, SentenceTransformer  # noqa: F401
        from peft import PeftModel  # noqa: F401
        print("  sentence_transformers and peft imports OK")
    except Exception as e:
        ok = False
        print(f"  import FAILED: {e}")
    return ok


def check_gpu():
    print("\n--- GPU (informational) ---")
    line()
    try:
        import torch
        if torch.cuda.is_available():
            free_b, total_b = torch.cuda.mem_get_info(0)
            print(f"  {torch.cuda.get_device_name(0)} | free {free_b/1e9:.1f} GB of {total_b/1e9:.1f} GB")
            try:
                import bitsandbytes as bnb
                y = bnb.nn.Linear4bit(4, 4).cuda()(torch.randn(4, 4).cuda())
                print(f"  bitsandbytes 4-bit forward OK {tuple(y.shape)}")
            except Exception as e:
                print(f"  bitsandbytes 4-bit test failed: {e}")
        else:
            print("  No GPU visible. Fine for Stages 0 to 5; needed for Stages 6 and 7.")
    except Exception as e:
        print(f"  GPU check error: {e}")


def reexec_in_venv():
    # Running with the wrong interpreter (e.g. the base conda python) reports every package as missing.
    # If the RAG venv exists and we are not in it, restart this script with the venv's python.
    venv_python = VENV_DIR / "bin" / "python"
    already = Path(sys.prefix).resolve() == VENV_DIR.resolve()
    if venv_python.exists() and not already and not os.environ.get("CHECK_NO_REEXEC"):
        print(f"Not running in the RAG venv; restarting with {venv_python}", flush=True)
        os.environ["CHECK_NO_REEXEC"] = "1"      # prevent a loop
        os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]])


def main():
    reexec_in_venv()
    print("=" * 60)
    print(" Assignment 2B environment verification")
    print("=" * 60)
    results = [("Interpreter", check_interpreter()), ("Package versions", check_packages()),
               ("Functional smoke tests", check_functional())]
    check_gpu()
    print("\n--- Summary ---")
    line()
    for name, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}]  {name}")
    if all(ok for _, ok in results):
        print("\n All required checks passed.")
        sys.exit(0)
    print("\n Some checks failed. Re-run: bash kubeflow/setup_env.sh")
    sys.exit(1)


if __name__ == "__main__":
    main()
