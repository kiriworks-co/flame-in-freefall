# Deployment Guide — Local Execution, Streamlit Community Cloud & GitHub Pages

## 1. Local Execution (Recommended First Check)
Requires **Python 3.11** (matching `.python-version`).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8511 --server.address 127.0.0.1
```

Open `http://127.0.0.1:8511`.  
On cold start, `ensure_scientific_bootstrap()` initializes `data/scientific.sqlite3` and `data/search.sqlite3` locally from preserved NASA files in ~5–6 seconds without requiring external API keys or model downloads.

---

## 2. Hosting Architecture: Streamlit Community Cloud vs. GitHub Pages
- **Streamlit Community Cloud (Interactive App)**: Runs the Python 3.11 + SQLite + PyMuPDF + Plotly interactive application directly from `app.py`.
- **GitHub Pages (Optional Static Showcase)**: GitHub Pages hosts static HTML/CSS/JS only (`docs/index.html`) as a lightweight bilingual entry page linking to the deployed Streamlit Cloud URL.

---

## 3. Repository Configuration & Cold-Start Behavior
- `.python-version`: pins Python `3.11`.
- `.streamlit/config.toml`: configures **Aerospace Laboratory Daylight** theme tokens (`#B84A24`, `#F8F9FA`, `#EFF2F5`, `#0F1D2B`), sets `[client] toolbarMode = "viewer"` and `showErrorDetails = "none"` to hide Streamlit developer chrome, and omits localhost-only bindings so cloud reverse proxies attach cleanly.
- `app.py`: uses `initial_sidebar_state="auto"` so desktop opens with navigation visible while narrow mobile viewports collapse the sidebar cleanly.
- Preserved NASA artifacts (`data/psi_downloads/`, `data/experimentos/`, `resources/official/`, `resources/manifests/`) fit directly inside standard Git without Git LFS.
- Generated SQLite databases (`data/scientific.sqlite3`, `data/search.sqlite3`), virtual environments (`.venv/`), and secrets (`.env`) are excluded via `.gitignore`.
- Public cloud hosts (`STREAMLIT_SHARING_MODE`, `/mount/src`, or `PSI_READONLY_MODE=1`) trigger `is_public_readonly()` automatically: public file uploads, document reprocessing, and archive mutations are disabled, while chart inspection choices remain ephemeral inside per-user `st.session_state`.

---

## 4. Optional Environment Variables & Secrets (`.env` / Streamlit Secrets)
All external AI integrations are **optional and disabled by default**. Never commit real credentials to Git.

```toml
# Read-only public archive enforcement
PSI_READONLY_MODE = "1"

# Optional Google Gemini API (for Scientific Assistant grounded synthesis)
# GEMINI_API_KEY = "AIza..."
# GEMINI_MODEL = "gemini-2.5-flash"

# Optional OpenAI-compatible RAG / VLM fallback endpoints
# RAG_BASE_URL = "https://..."
# RAG_MODEL = "..."
# RAG_API_KEY = "..."
# VLM_BASE_URL = "https://..."
# VLM_MODEL = "..."
# VLM_API_KEY = "..."
```

### Runtime Privacy & Cost Guardrails
- `src/gemini_provider.py` filters retrieved passages through `filter_public_nasa_evidence()`, blocking private `local_upload` excerpts from external API transmission.
- Built-in rolling limits enforce `10` Gemini calls/minute and `40` calls/session with cached repeated queries and automatic fallback to offline NASA citations on errors/timeouts.
- `validate_claims()` requires every generated sentence to cite real retrieved sources and match reported numeric values before appearing in chat.
- Leave `requirements-models.txt` / `RAG_EMBEDDING_MODEL` omitted on standard free cloud containers so retrieval uses zero-weight deterministic offline EN/PT `lexical-vectors` + SQLite `FTS5` cleanly.

---

## 5. Deploying to Streamlit Community Cloud
1. Merge or select branch `main` (or `feat/spaceapps-public-release`) on your GitHub repository.
2. Open [https://share.streamlit.io/](https://share.streamlit.io/) and select **Create app**.
3. Configure:
   - **Repository**: `<owner>/<repo>`
   - **Branch**: `main` (or `feat/spaceapps-public-release`)
   - **Main file path**: `app.py`
   - **Python version**: `3.11`
4. *(Optional)* Add `PSI_READONLY_MODE = "1"` (and optional `GEMINI_API_KEY`) under **Advanced settings → Secrets**.
5. Deploy and verify:
   - Default load renders `"Explore the Science of Fire in Space"` with `Where you are`, `← Back`, `🏠 Home`, `Language: EN → PT-BR`, `9` PSI Studies, `16` NASA Files, `31` Tables, and `1,517` offline index chunks (or `2,711` when local semantic embeddings are active).
   - No `Deploy` button or raw tracebacks appear (`toolbarMode = "viewer"`, `showErrorDetails = "none"`).
   - `Data Explorer` and `Sources & Methodology` display read-only protection cleanly.

---

## 6. Publishing the Optional GitHub Pages Card
1. Update the launch button `href` inside `docs/index.html` to point to your live `https://<app-name>.streamlit.app/` URL.
2. Under GitHub **Settings → Pages**, deploy from branch `main` folder `/docs`.
