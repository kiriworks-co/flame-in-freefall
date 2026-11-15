"""Import downloaded, hash-verified NASA files; no download occurs here."""
import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.pipeline import ingest_downloads  # noqa: E402

if __name__ == "__main__":
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-index", action="store_true")
    args = parser.parse_args()
    result = ingest_downloads(index_search=not args.no_index)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    raise SystemExit(2 if result["errors"] else 0)
