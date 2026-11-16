"""Safe local credential configuration helper for optional Google Gemini API integration."""
from __future__ import annotations

import argparse
import getpass
import json
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.gemini_provider import DEFAULT_GEMINI_MODEL, gemini_model_name, gemini_status_summary  # noqa: E402

_KEY_SAFE_RE = re.compile(r"^[^\s\x00-\x1f\x7f\"']{10,256}$")
_MODEL_SAFE_RE = re.compile(r"^[a-zA-Z0-9._-]{3,80}$")


def _upsert_env_values(env_path: Path, updates: dict[str, str]) -> None:
    """Update or append key=value entries in an env file while preserving all other variables."""
    existing_lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    seen: set[str] = set()
    output: list[str] = []
    for line in existing_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in line:
            key = line.split("=", 1)[0].strip()
            if key in updates:
                output.append(f"{key}={updates[key]}")
                seen.add(key)
                continue
        output.append(line)
    for key, val in updates.items():
        if key not in seen:
            output.append(f"{key}={val}")
    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.write_text("\n".join(output).rstrip("\n") + "\n", encoding="utf-8")


def _write_streamlit_secrets(secrets_path: Path, api_key: str, model: str) -> None:
    """Write or update .streamlit/secrets.toml without exposing credentials in stdout."""
    lines = [
        "# Local Streamlit secrets (gitignored — never commit this file).",
        'PSI_READONLY_MODE = "0"',
        f'GEMINI_API_KEY = "{api_key}"',
        f'GEMINI_MODEL = "{model}"',
    ]
    secrets_path.parent.mkdir(parents=True, exist_ok=True)
    secrets_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Configure or inspect optional Google Gemini API credentials for Flame in Freefall."
    )
    parser.add_argument("--status", action="store_true", help="Report non-secret Gemini configuration status and exit.")
    parser.add_argument("--key", type=str, default=None, help="Google AI Studio API key (omit for hidden prompt).")
    parser.add_argument("--model", type=str, default=DEFAULT_GEMINI_MODEL, help=f"Gemini model ID (default: {DEFAULT_GEMINI_MODEL}).")
    parser.add_argument("--streamlit-secrets", action="store_true", help="Also write .streamlit/secrets.toml alongside .env.")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env", help="Target .env file path.")
    args = parser.parse_args(argv)

    env_path = args.env_file.resolve()
    if env_path.exists():
        load_dotenv(env_path, override=False)

    if args.status:
        summary = gemini_status_summary("en")
        print(
            json.dumps(
                {
                    "status": summary["status"],
                    "model": gemini_model_name(),
                    "env_file_exists": env_path.exists(),
                    "secrets_template_exists": (ROOT / ".streamlit" / "secrets.toml.example").exists(),
                },
                indent=2,
            )
        )
        return 0

    model = str(args.model or DEFAULT_GEMINI_MODEL).strip()
    if not _MODEL_SAFE_RE.fullmatch(model):
        print(f"Invalid model identifier '{model}'. Use e.g. {DEFAULT_GEMINI_MODEL}.", file=sys.stderr)
        return 2

    raw_key = args.key if args.key is not None else getpass.getpass("Google AI Studio API Key (input hidden): ")
    key = str(raw_key or "").strip()
    if not _KEY_SAFE_RE.fullmatch(key):
        print("Invalid or empty API key. Obtain a key from Google AI Studio and try again.", file=sys.stderr)
        return 2

    if not key.startswith("AIza"):
        print("Notice: Google AI Studio API keys typically begin with 'AIza'. Saving anyway for live check.")

    _upsert_env_values(env_path, {"GEMINI_API_KEY": key, "GEMINI_MODEL": model})
    if args.streamlit_secrets:
        _write_streamlit_secrets(ROOT / ".streamlit" / "secrets.toml", key, model)

    print(f"Configured Gemini model '{model}' in {env_path.name} (API key value hidden).")
    if args.streamlit_secrets:
        print("Updated .streamlit/secrets.toml (gitignored).")
    print("Next: run `python scripts/gemini_live_check.py` to verify live grounded retrieval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
