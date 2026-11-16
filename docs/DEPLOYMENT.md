# Deployment Guide — Local Execution, Streamlit Community Cloud & GitHub Pages

## 1. Local Execution & Owner Verification Checklist
Requires **Python 3.11+** (`.python-version` pins `3.11` for cloud compatibility; locally verified on Python `3.12.14`).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8511 --server.address 127.0.0.1
```

Open `http://127.0.0.1:8511`.  
On cold start, `ensure_scientific_bootstrap()` initializes `data/scientific.sqlite3` and `data/search.sqlite3` locally from preserved NASA artifacts without requiring external API keys or model downloads.

### Optional Google Gemini Setup (Local or Cloud)
1. Obtain a key from Google AI Studio.
2. Run locally:
   ```powershell
   .\.venv\Scripts\python.exe scripts/setup_gemini.py
   .\.venv\Scripts\python.exe scripts/gemini_live_check.py --require-key
   ```
3. Or copy `.streamlit/secrets.toml.example` into Streamlit Community Cloud **App Settings → Secrets**.

---

## 2. Hosting Architecture: Streamlit Community Cloud vs. GitHub Pages
- **Streamlit Community Cloud (Interactive Python Application):** Runs `app.py` with Python `3.11`, SQLite, PyMuPDF, Pint, and Plotly directly from GitHub.
- **GitHub Pages (Optional Static Card):** Hosts static HTML/CSS/JS only (`docs/index.html`) linking out to the deployed Streamlit Cloud app. The Python app is completely independent of GitHub Pages.

---

## 3. Repository Configuration & Public Read-Only Behavior
- `.python-version`: pins Python `3.11`.
- `.streamlit/config.toml`: configures **Aerospace Laboratory Daylight** theme tokens (`#B84A24`, `#F8F9FA`, `#EFF2F5`, `#0F1D2B`), sets `[client] toolbarMode = "minimal"` and `showErrorDetails = "none"` to hide Streamlit developer chrome/three-dot menus, and omits localhost-only bindings so cloud reverse proxies attach cleanly.
- `.streamlit/secrets.toml.example`: safe commented TOML template for Streamlit Cloud Secrets (`.streamlit/secrets.toml` and `.env` are gitignored).
- `app.py`: uses `initial_sidebar_state="auto"` so desktop opens with navigation visible while mobile collapses cleanly.
- Preserved NASA artifacts (`data/psi_downloads/`, `data/experimentos/`, `resources/official/`, `resources/manifests/`) are stored directly in Git (with `.gitattributes` preserving original bytes).
- Generated SQLite databases (`data/scientific.sqlite3`, `data/search.sqlite3`), virtual environments (`.venv/`), temporary folders (`tmp/`), and `.env` / `.streamlit/secrets.toml` are excluded via `.gitignore`.
- Public cloud hosts (`STREAMLIT_SHARING_MODE`, `/mount/src`, or `PSI_READONLY_MODE=1`) trigger `is_public_readonly()` automatically: public file uploads, document reprocessing, and archive mutations are disabled, while chart inspection choices remain ephemeral inside per-user `st.session_state`.

---

## 4. Runtime Privacy & Cost Guardrails
- `src/gemini_provider.py` filters retrieved passages through `filter_public_nasa_evidence()`, blocking private `local_upload` excerpts from external API transmission.
- Built-in rolling limits enforce **`10` Gemini calls/minute**, **`250` calls/day**, and **`40` calls/session** with cached repeated queries and automatic fallback to offline NASA citations on errors/timeouts.
- `validate_claims()` requires every generated quote and optional 1-sentence explanation to cite real retrieved sources, preserve evidence roles (`condition`, `simulation`, `reported_result`, `metadata`), and match reported numeric values before appearing in chat.
- Leave `requirements-models.txt` / `RAG_EMBEDDING_MODEL` omitted on standard free cloud containers so retrieval uses zero-weight deterministic offline EN/PT lexical vectors + SQLite `FTS5` cleanly within free-tier memory limits.

---

## 5. Deploying to Streamlit Community Cloud (When Ready)
1. Verify local checks pass and push `feat/spaceapps-public-release` (or merge to `main`) to your GitHub repository.
2. Open [https://share.streamlit.io/](https://share.streamlit.io/) and select **Create app**.
3. Configure:
   - **Repository**: `<owner>/<repo>`
   - **Branch**: `feat/spaceapps-public-release` (or `main`)
   - **Main file path**: `app.py`
   - **Python version**: `3.11`
4. Under **Advanced settings → Secrets**, add:
   ```toml
   PSI_READONLY_MODE = "1"
   # Optional:
   # GEMINI_API_KEY = "AIza..."
   # GEMINI_MODEL = "gemini-2.5-flash"
   ```
5. Deploy and verify on the live URL:
   - Default load renders `"Explore the Science of Fire in Space"`, deep-navy hero with `1g vs ~0g` visual diagram, single `EN | PT-BR` selector, `12` NASA PSI Studies, `40` Preserved NASA Files, `117` Extracted Tables, and offline indexed passages.
   - No `Deploy` button, developer CLI commands, or raw tracebacks appear.
   - `Data Explorer` and `Sources & Methodology` display read-only protection cleanly.

---

## 6. Owner Local Verification & Submission Checklist
- [ ] Review live app locally at `http://127.0.0.1:8511` and independently review scientific interpretations against the original NASA sources.
- [ ] *(Optional)* Configure personal Google AI Studio key with `python scripts/setup_gemini.py` and verify via `python scripts/gemini_live_check.py --require-key`.
- [ ] Verify clean Git status and absence of secrets (`git status -sb`, `git ls-files .env .streamlit/secrets.toml`).
- [ ] Push verified branch to your own GitHub repository and deploy on Streamlit Community Cloud.
- [ ] *(Optional)* Update the launch URL inside `docs/index.html` and enable GitHub Pages on `/docs`.
- [ ] Submit text from [SUBMISSION_DESCRIPTION_EN.md](SUBMISSION_DESCRIPTION_EN.md) on the Space Apps portal.
