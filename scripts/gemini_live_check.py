"""Non-destructive diagnostic script to verify live Google Gemini grounded retrieval or offline fallback."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.assistant import answer  # noqa: E402
from src.gemini_provider import gemini_configured, gemini_model_name  # noqa: E402
from src.retrieval import RetrievalIndex  # noqa: E402


def run_live_check(env_file: Path | None = None) -> dict[str, object]:
    """Check whether Gemini is configured and, if so, run one grounded PSI-69 verification query."""
    target_env = env_file or (ROOT / ".env")
    if target_env.exists():
        load_dotenv(target_env, override=False)

    model = gemini_model_name()
    if not gemini_configured():
        return {
            "status": "UNCONFIGURED",
            "model": model,
            "fallback_mode": "offline-evidence",
            "next_step": "Run `python scripts/setup_gemini.py` or set GEMINI_API_KEY in .env / Streamlit Secrets.",
        }

    index = RetrievalIndex()
    result = answer(
        "What oxygen mole fraction was used in FLEX?",
        index=index,
        study_ids=["PSI-69"],
        language="en",
        use_llm=True,
        session_id="gemini-live-check",
    )
    provider_status = str(result.get("provider_status") or "unknown")
    claims = list(result.get("claims") or [])
    evidence = list(result.get("evidence") or [])
    status = "LIVE_VERIFIED" if provider_status == "gemini_verified" and claims else "FALLBACK_AFTER_ERROR"
    return {
        "status": status,
        "model": model,
        "mode": str(result.get("mode") or ""),
        "provider_status": provider_status,
        "evidence_count": len(evidence),
        "verified_claims_count": len(claims),
        "warnings": [str(w) for w in result.get("warnings") or []],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify live Google Gemini grounded synthesis or offline mode.")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env", help="Path to .env file.")
    parser.add_argument("--require-key", action="store_true", help="Exit non-zero if Gemini is unconfigured or fails live check.")
    args = parser.parse_args(argv)

    report = run_live_check(args.env_file.resolve())
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.require_key and report["status"] != "LIVE_VERIFIED":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
