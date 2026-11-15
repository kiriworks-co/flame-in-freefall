#!/usr/bin/env python3
"""Explicit download of a public multilingual embedding model, outside the repo."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PROJECT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configure", action="store_true", help="Set the local model path in .env; preserve other keys")
    args = parser.parse_args()
    from huggingface_hub import HfApi, snapshot_download

    info = HfApi(token=False).model_info(MODEL)
    local = snapshot_download(MODEL, revision=info.sha, token=False,
                              allow_patterns=["*.json", "model.safetensors", "*.model", "tokenizer*", "vocab.txt",
                                              "1_Pooling/*", "README.md"])
    record = {"model": MODEL, "revision": info.sha, "local_path": str(local), "license": "Apache-2.0",
              "model_card": f"https://huggingface.co/{MODEL}",
              "retrieved_utc": datetime.now(timezone.utc).isoformat()}
    output = PROJECT / "data" / "embedding_model.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2), encoding="utf-8")
    if args.configure:
        env_path = PROJECT / ".env"
        lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
        lines = [line for line in lines if not line.startswith("RAG_EMBEDDING_MODEL=")]
        lines.append(f"RAG_EMBEDDING_MODEL={Path(local).as_posix()}")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    print("Rebuild the index: python scripts/ingest_nasa.py")


if __name__ == "__main__":
    main()
