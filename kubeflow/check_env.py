#!/usr/bin/env python
"""
kubeflow/check_env.py  (Assignment 2B)

Verifies the RAG environment created by kubeflow/setup_env.sh.

    /home/group157/venv-rag/bin/python kubeflow/check_env.py

GPU checks are informational: Stages 0 to 5 run on CPU, only Stages 6 and 7 need a GPU.
Exits 0 when every package check passes, 1 otherwise.
"""
import importlib
import sys

EXPECTED = {            # module name -> required version prefix (None = any)
    "torch": "2.",
    "transformers": "4.46.3",
    "tokenizers": "0.20.3",
    "accelerate": "1.1.1",
    "safetensors": "0.4.5",
    "huggingface_hub": "0.26.2",
    "peft": "0.13.2",
    "bitsandbytes": "0.44.1",
    "sentence_transformers": "3.3.1",
    "faiss": None,
    "rank_bm25": None,
    "sklearn": "1.5.2",
    "pandas": "2.2.3",
    "numpy": "2.",
    "tqdm": "4.67.0",
}


def line(n=60):
    print("-" * n)


def check_interpreter():
    print("\n--- Interpreter ---")
    line()
    print(f"  python executable: {sys.executable}")
    if "venv-rag" in sys.executable:
        print("  OK: running inside the RAG venv.")
    else:
        print("  WARNING: not the RAG venv interpreter (select 'Python (RAG venv)' in the notebook).")
    return True


def check_imports():
    print("\n--- Package imports and versions ---")
    line()
    ok = True
    for pkg, prefix in EXPECTED.items():
        try:
            mod = importlib.import_module(pkg)
            ver = str(getattr(mod, "__version__", "(no __version__)"))
            bad = bool(prefix) and not ver.startswith(prefix)
            ok &= not bad
            print(f"  {pkg:<24}{ver:<16}{'MISMATCH (expected ' + prefix + ')' if bad else 'OK'}")
        except ImportError as e:
            ok = False
            print(f"  {pkg:<24}MISSING         ({e})")
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
        scores, ids = index.search(np.eye(4, dtype="float32")[:1], 1)
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


def main():
    print("=" * 60)
    print(" Assignment 2B environment verification")
    print("=" * 60)
    results = [("Interpreter", check_interpreter()), ("Package versions", check_imports()),
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
