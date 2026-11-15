# Deployment Guide — Streamlit Community Cloud & GitHub Pages

## 1. Why Two Hosting Targets?
- **GitHub Pages** serves only static HTML/CSS/JS files and cannot run Python, SQLite, PyMuPDF, or Streamlit (`streamlit run app.py`).
- **Streamlit Community Cloud** executes the live Python 3.11 + SQLite + Plotly interactive scientific application directly from the GitHub repository.
- Optionally, GitHub Pages can host `docs/index.html` as a lightweight bilingual project landing page linking straight to the live Streamlit Community Cloud URL.

---

## 2. Repository Readiness & Cold-Start Behavior
This repository is pre-configured for reproducible, zero-secret cold start:
- `.python-version` pins `3.11`.
- `.streamlit/config.toml` sets theme colors and omits a localhost-only server binding (`address = "127.0.0.1"` removed) so reverse proxies bind cleanly.
- Committed NASA artifacts (`data/psi_downloads/`, `data/experimentos/`, `resources/official/`, `resources/manifests/`) total ~19.7 MB (largest single file ~3.7 MB), fitting cleanly in standard Git without Git LFS.
- Generated SQLite databases (`data/scientific.sqlite3`, `data/search.sqlite3`) and `.env` are gitignored. On first boot in a clean cloud container, `app.py` calls cached `ensure_scientific_bootstrap()`, initializing both databases locally from committed artifacts in ~5–6 seconds (offline `lexical-vectors` mode by default, zero network calls or paid API keys needed).
- When running on Streamlit Cloud (`STREAMLIT_SHARING_MODE` or `/mount/src` or `PSI_READONLY_MODE=1`), `is_public_readonly()` activates automatically: public file uploads, document reprocessing, archive mutations, and experiment creation/editing are disabled, while chart column inspection overrides stay ephemeral in per-user `st.session_state`.

---

## 3. Deploying to Streamlit Community Cloud
1. Ensure branch `feat/spaceapps-public-release` is merged into `main` (or deploy directly from `feat/spaceapps-public-release`) on your public GitHub repository.
2. Open [https://share.streamlit.io/](https://share.streamlit.io/) and sign in with GitHub.
3. Click **Create app** → **Yup, I have an app**:
   - **Repository**: `<owner>/<repo>`
   - **Branch**: `main` (or `feat/spaceapps-public-release`)
   - **Main file path**: `app.py`
   - **Python version** (Advanced settings): `3.11`
4. *(Optional)* Under **Advanced settings → Secrets**, leave blank for pure Evidence Retrieval mode, or add read-only mode + optional OpenAI-compatible endpoints if desired:
   ```toml
   PSI_READONLY_MODE = "1"
   # Optional only — leave omitted to run 100% free/offline:
   # RAG_BASE_URL = "https://..."
   # RAG_MODEL = "..."
   # RAG_API_KEY = "..."
   # VLM_BASE_URL = "https://..."
   # VLM_MODEL = "..."
   # VLM_API_KEY = "..."
   ```
   Do **not** install `requirements-models.txt` unless your cloud instance explicitly provides sufficient RAM/storage and a pre-staged `RAG_EMBEDDING_MODEL`.
5. Click **Deploy!** and verify:
   - Default page loads in English (`Flame in Freefall: Microgravity Combustion Explorer`).
   - Metrics show `9` PSI Studies, `16` Preserved NASA Files, `31` Extracted Tables, and `1517` Indexed Chunks.
   - Sidebar switcher toggles `English (EN)` ↔ `Português (PT-BR)`.
   - `Data Explorer` and `Sources & Methodology` display the public read-only notice and disallow file uploads.

---

## 4. Publishing the Optional Static Landing Page (GitHub Pages)
1. Update the `"Launch Interactive Streamlit App"` `<a href="...">` URL in `docs/index.html` to your deployed `https://<app-name>.streamlit.app/` URL.
2. In your GitHub repository: **Settings → Pages → Build and deployment**:
   - **Source**: Deploy from a branch
   - **Branch**: `main` → `/docs` folder
3. Save and open the generated `https://<owner>.github.io/<repo>/` URL.
