# Design System — Flame in Freefall (`PSI Flame Microgravity`)

Single source of visual truth: [`src/design_system.py`](file:///c:/Users/kiriyama/Desktop/Projects/PSI_Flame_Microgravity_Codex_Kit/PROJETO%20TESTE%20FLAME%20MICROGRAVITY/src/design_system.py) and [`.streamlit/config.toml`](file:///c:/Users/kiriyama/Desktop/Projects/PSI_Flame_Microgravity_Codex_Kit/PROJETO%20TESTE%20FLAME%20MICROGRAVITY/.streamlit/config.toml).

---

## 1. Visual Direction & Color Palette

Theme: **Aerospace Laboratory Daylight** — calm editorial ivory/slate surfaces with high-contrast aerospace navy typography and restrained thermal/scientific accents inspired by orbital flight telemetry and microgravity blue-amber flames.

| Token | Hex | Contrast on `#FFFFFF` / `#F8F9FA` | Semantic Usage |
|---|---|---|---|
| `bg_canvas` | `#F8F9FA` | Base canvas | Page background in `.streamlit/config.toml` |
| `bg_surface` | `#FFFFFF` | Surface base | Cards, metric tiles, evidence blocks, chat turns |
| `bg_subtle` | `#EFF2F5` | Surface tint | Sidebar, context bar, secondary callouts |
| `border_subtle` | `#D9E0E6` | Structural hairline | Card outlines, pill borders, dividers |
| `ink_primary` | `#0F1D2B` | **~16.5:1 (AAA)** | Headings, titles, primary body text |
| `ink_secondary` | `#3E4C59` | **~8.6:1 (AAA)** | Subtitles, lead copy, structured labels |
| `ink_muted` | `#52606D` | **~6.2:1 (AA+)** | Captions, timestamps, provenance hashes |
| `accent_flame` | `#B84A24` | **~4.8:1 (AA)** | Primary CTA, focus rings, suppression / thermal highlight |
| `accent_science` | `#1D5B86` | **~6.9:1 (AA+)** | Links, prevention/research badges, secondary charts |
| `status_success` | `#1F7A5C` | **~5.1:1 (AA)** | Verified SHA-256, grounded quotes, detection badges |
| `status_warning` | `#9A5B13` | **~5.2:1 (AA)** | Scientific caveats, unit warnings (`Burning rate; mm`), partial PDFs |

---

## 2. Typography & Scale

- **UI & Editorial Sans:** `"Inter", "Segoe UI", system-ui, -apple-system, sans-serif` (configured cleanly with balanced headline wrapping `text-wrap: balance`).
- **Scientific Data & Provenance Mono:** `"JetBrains Mono", "Cascadia Code", ui-monospace, monospace` for document IDs, DOI links, CSV headers, and SHA-256 digests.
- **Numeric Discipline:** `font-variant-numeric: tabular-nums` enforced across all `st.metric` readouts and `st.dataframe` tables.
- **Type Hierarchy:**
  - Page `h1`: crisp `letter-spacing: -0.02em`, deep navy `#0F1D2B`.
  - Lead paragraph (`.psi-lead`): `1.06rem`, `line-height: 1.58`, `color: #3E4C59`.
  - Section headers `h2`/`h3`: clear hierarchy with `>= 0.75rem` breathing margin above content blocks.

---

## 3. Spacing, Layout & Chrome Rules

- **Top Safe Clearance:** `[data-testid="stMainBlockContainer"]` sets `max-width: 88rem`, `padding-top: 3.25rem` (`3.5rem` on `<= 48rem`), preventing header/title collision at `100%` and `200%` zoom.
- **Viewer Toolbar Mode:** `.streamlit/config.toml` enables `[client] toolbarMode = "viewer"` and `showErrorDetails = "none"` to remove Streamlit developer `Deploy` / rerun clutter while keeping sidebar expand/collapse accessible.
- **Card Discipline:** Maximum 1 border level per card (`border: 1px solid #D9E0E6`, `border-radius: 0.75rem`, zero nested-cards-inside-cards).
- **Focus & Touch Targets:** Interactive buttons and segmented pills enforce `min-height: 2.65rem` and a visible `3px solid #B84A24` focus ring.

---

## 4. Reusable Components (`src/design_system.py`)

1. **`render_context_navigation_bar(...)`**: Top context strip showing *Where you are* breadcrumb, active journey badge (if any), quick `Home` and `← Back` actions, and active `EN | PT-BR` switcher.
2. **`render_hero_banner(...)`**: Discovery-first header framing the title, subtitle, and plain-language overview in <= 10 seconds.
3. **`render_pillar_badge(...)`**: Color-coded badge for **Prevention** (`#1D5B86`), **Detection** (`#1F7A5C`), **Suppression** (`#B84A24`), and **Context** (`#52606D`).
4. **`render_five_question_framework(...)`**: Structured 5-part guided comprehension panel (*What am I exploring? · Why does it matter? · What does the NASA evidence show? · What can I conclude? · What are the limitations?*).
5. **`style_scientific_figure(fig, ...)`**: Shared Plotly visual standard with high-contrast palette, clean subtle `#E7ECEF` gridlines, bottom horizontal legend, tabular tick labels, and generous title/margin spacing.
