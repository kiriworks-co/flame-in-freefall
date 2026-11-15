# Public Release Verification Checklist

Check every item before pushing `main` / `feat/spaceapps-public-release` publicly:

- [ ] **Git repository isolation**: Confirm `git rev-parse --show-toplevel` points strictly inside the project root (`PROJETO TESTE FLAME MICROGRAVITY`), never an ancestor folder.
- [ ] **Zero secrets or user paths**: Run `git grep -iE "(sk-|api_key|bearer |C:\\\\Users|/home/[a-z])"` across tracked files and inspect `.gitignore` (`.env`, `.venv`, `data/*.sqlite3*`, `docs/junit.xml`).
- [ ] **Static checks green**: `ruff check app.py src scripts tests`, `mypy`, `compileall`, and `pip check` exit `0`.
- [ ] **Full automated suite green**: `pytest -q` passes with zero failures/skips in the release environment.
- [ ] **Clean cold-start verified**: App boots offline from a fresh directory copy without `.env` or pre-built `.sqlite3` files (`AppTest` + `ensure_scientific_bootstrap()`).
- [ ] **Public read-only safety verified**: With `PSI_READONLY_MODE=1`, uploads, experiment edits/creation, and manual ingestion buttons are disabled/hidden.
- [ ] **Bilingual parity verified**: `TRANSLATIONS["en"]` and `TRANSLATIONS["pt"]` have matching key sets, default is English, switcher updates active view cleanly without mutating original NASA titles, IDs, DOIs, or values.
- [ ] **No fabricated AI claims**: When `RAG_API_KEY` / `VLM_API_KEY` are absent, UI explicitly states Evidence Retrieval / Local Preview mode.
- [ ] **Update `docs/index.html` CTA URL** with the final `https://<app-name>.streamlit.app` link after Streamlit Community Cloud deployment succeeds.
