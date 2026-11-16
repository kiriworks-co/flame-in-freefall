"""Centralized design tokens, accessible styling, navigation bar, visual hero, and figure polish."""
from __future__ import annotations

import html
from collections.abc import Callable
from typing import Any

import plotly.graph_objects as go
import streamlit as st

DESIGN_TOKENS: dict[str, str] = {
    "bg_canvas": "#F8F9FA",
    "bg_surface": "#FFFFFF",
    "bg_subtle": "#EFF2F5",
    "border_subtle": "#D9E0E6",
    "ink_primary": "#0F1D2B",
    "ink_secondary": "#3E4C59",
    "ink_muted": "#52606D",
    "accent_flame": "#B84A24",
    "accent_science": "#1D5B86",
    "status_success": "#1F7A5C",
    "status_warning": "#9A5B13",
    "gridline": "#E7ECEF",
}

PLOTLY_SCIDATA_COLORWAY: list[str] = [
    "#B84A24",
    "#1D5B86",
    "#1F7A5C",
    "#7B4B94",
    "#C07A1A",
    "#2E6F95",
]

_PILLAR_STYLES: dict[str, tuple[str, str]] = {
    "prevention": ("#EBF3F9", "#1D5B86"),
    "prevenção": ("#EBF3F9", "#1D5B86"),
    "detection": ("#EAF5F0", "#1F7A5C"),
    "detecção": ("#EAF5F0", "#1F7A5C"),
    "suppression": ("#FBEDE8", "#B84A24"),
    "supressão": ("#FBEDE8", "#B84A24"),
    "context": ("#EFF2F5", "#3E4C59"),
    "contexto": ("#EFF2F5", "#3E4C59"),
}


def inject_global_styles() -> None:
    """Inject static, accessible responsive styling tokens without external interpolation."""
    st.html(
        """<meta name="google" content="notranslate">
        <style>
        /* Prevent horizontal viewport overflow across desktop, tablet, and mobile */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            max-width: 100%;
            overflow-x: clip;
        }
        /* Tight, balanced top clearance without excessive empty whitespace */
        [data-testid="stMainBlockContainer"] {
            max-width: min(88rem, 100%);
            box-sizing: border-box;
            padding-top: 1.25rem;
            padding-bottom: 2.75rem;
            padding-inline: 2.25rem !important;
        }
        @media (min-width: 64.01rem) {
            [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"] {
                flex-wrap: nowrap !important;
            }
            [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                min-width: 0 !important;
            }
        }
        [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"],
        [data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"],
        [data-testid="stMainBlockContainer"] [data-testid="stTabs"] {
            max-width: 100%;
            min-width: 0;
        }
        [data-testid="stMainBlockContainer"] [data-testid="stColumn"] {
            min-width: 0;
        }
        [data-testid="stTabs"] [role="tablist"] {
            flex-wrap: wrap !important;
            max-width: 100%;
            row-gap: 0.25rem;
        }
        [data-testid="stPlotlyChart"],
        [data-testid="stDataFrame"],
        [data-testid="stCodeBlock"],
        pre {
            max-width: 100% !important;
            min-width: 0 !important;
        }
        /* Keep Streamlit header subtle and hide unnecessary developer toolbar / menu */
        [data-testid="stHeader"] {
            background: transparent !important;
            height: 2.5rem !important;
        }
        [data-testid="stToolbarActions"],
        [data-testid="stMainMenu"],
        [data-testid="stDeployButton"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"] {
            display: none !important;
        }
        h1, h2, h3 {
            color: #0F1D2B;
            text-wrap: balance;
            letter-spacing: -0.02em;
        }
        .psi-lead {
            font-size: 1.05rem;
            color: #3E4C59;
            margin-top: -0.35rem;
            margin-bottom: 0.9rem;
            line-height: 1.52;
            max-width: 72ch;
        }
        /* Aerospace Navy Hero & Scientific Schematic */
        .psi-hero-shell {
            background: linear-gradient(135deg, #0F1D2B 0%, #152B40 100%);
            border: 1px solid #243B53;
            border-left: 5px solid #B84A24;
            border-radius: 0.85rem;
            padding: 1.25rem 1.45rem;
            margin-bottom: 1rem;
            color: #F8F9FA;
            display: grid;
            grid-template-columns: 1.15fr 1fr;
            gap: 1.25rem;
            align-items: center;
        }
        .psi-hero-kicker {
            display: inline-block;
            font-size: 0.74rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #F3A683;
            margin-bottom: 0.45rem;
        }
        .psi-hero-text {
            color: #E6EDF3;
            font-size: 0.96rem;
            line-height: 1.56;
            margin: 0 0 0.85rem 0;
        }
        .psi-hero-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
        }
        .psi-hero-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.24rem 0.65rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            background: rgba(29, 91, 134, 0.38);
            border: 1px solid #59A9DD;
            color: #F8F9FA;
        }
        .psi-hero-pill-flame {
            background: rgba(184, 74, 36, 0.35);
            border-color: #E77C46;
        }
        .psi-hero-diagram {
            background: #0B1622;
            border: 1px solid #243B53;
            border-radius: 0.75rem;
            padding: 0.7rem;
            width: 100%;
            box-sizing: border-box;
        }
        .psi-diag-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.65rem;
            margin-bottom: 0.6rem;
        }
        .psi-diag-card {
            background: #132336;
            border: 1px solid #2C4966;
            border-radius: 0.6rem;
            padding: 0.65rem 0.5rem;
            text-align: center;
        }
        .psi-diag-card-0g {
            border-color: #59A9DD;
        }
        .psi-diag-title {
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #F8F9FA;
            margin-bottom: 0.45rem;
        }
        .psi-diag-card-0g .psi-diag-title {
            color: #9CD0F5;
        }
        .psi-diag-stage {
            height: 4.9rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.45rem;
        }
        .psi-diag-arrow {
            color: #59A9DD;
            font-size: 0.95rem;
            font-weight: 700;
            line-height: 1;
        }
        .psi-flame-1g-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .psi-flame-1g {
            width: 1.85rem;
            height: 2.35rem;
            background: radial-gradient(circle at 50% 68%, #FFF3B0 0%, #F6C86E 28%, #E77C46 66%, #B84A24 100%);
            border-radius: 0 65% 65% 65%;
            transform: rotate(45deg);
            box-shadow: 0 0 14px rgba(231, 124, 70, 0.55);
            margin-bottom: 0.25rem;
        }
        .psi-fuel-base {
            width: 1.35rem;
            height: 0.35rem;
            background: #9FB3C8;
            border-radius: 2px;
        }
        .psi-flame-0g {
            width: 3.35rem;
            height: 3.35rem;
            border-radius: 999px;
            background: radial-gradient(circle, #F8F9FA 0%, #9CD0F5 24%, #E77C46 52%, rgba(29, 91, 134, 0.72) 78%, rgba(89, 169, 221, 0.15) 100%);
            border: 1.5px dashed #59A9DD;
            box-shadow: 0 0 16px rgba(89, 169, 221, 0.45);
        }
        .psi-diag-sub {
            font-size: 0.74rem;
            color: #CBD5E1;
            margin-top: 0.35rem;
        }
        .psi-diag-pipeline {
            background: #152B40;
            border: 1px solid #B84A24;
            border-radius: 0.5rem;
            padding: 0.4rem 0.65rem;
            text-align: center;
            font-size: 0.75rem;
            font-weight: 600;
            color: #F8F9FA;
        }
        /* Equal-height starting cards on Home */
        [data-testid="stHorizontalBlock"]:has(.psi-entry-card-body) {
            align-items: stretch !important;
        }
        [data-testid="stHorizontalBlock"]:has(.psi-entry-card-body) > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
            height: 100%;
        }
        [data-testid="stHorizontalBlock"]:has(.psi-entry-card-body) [data-testid="stVerticalBlockBorderWrapper"] {
            height: 100%;
            display: flex;
            flex-direction: column;
            background: #FFFFFF;
        }
        [data-testid="stHorizontalBlock"]:has(.psi-entry-card-body) [data-testid="stVerticalBlockBorderWrapper"] > div {
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        [data-testid="stHorizontalBlock"]:has(.psi-entry-card-body) [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
            height: 100%;
            justify-content: space-between;
        }
        .psi-entry-card-body {
            min-height: 9.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
        }
        .psi-entry-kicker {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            color: #1D5B86;
            text-transform: uppercase;
        }
        .psi-entry-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #0F1D2B;
            line-height: 1.3;
            margin: 0.1rem 0;
        }
        .psi-entry-desc {
            font-size: 0.93rem;
            color: #3E4C59;
            line-height: 1.48;
            margin: 0;
        }
        /* Context Breadcrumb & Top Bar */
        .psi-crumb-pill {
            display: inline-flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.4rem;
            max-width: 100%;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            background: #EFF2F5;
            border: 1px solid #D9E0E6;
            color: #0F1D2B;
            font-size: 0.85rem;
            font-weight: 600;
            line-height: 1.35;
            overflow-wrap: anywhere;
        }
        [data-testid="stMainBlockContainer"] button {
            max-width: 100%;
            height: auto;
        }
        [data-testid="stMainBlockContainer"] button p {
            white-space: normal;
            overflow-wrap: break-word;
            line-height: 1.25;
        }
        .psi-pillar-badge {
            display: inline-block;
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            border: 1px solid currentColor;
            margin-bottom: 0.35rem;
        }
        /* Tabular alignment for numbers and metrics */
        [data-testid="stMetricValue"], table {
            font-variant-numeric: tabular-nums;
        }
        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {
            white-space: normal !important;
            overflow-wrap: break-word;
            color: #3E4C59;
        }
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #D9E0E6;
            border-radius: 0.75rem;
            padding: 0.75rem 0.95rem;
        }
        [data-testid="stText"], [data-testid="stCaptionContainer"], p {
            overflow-wrap: anywhere;
        }
        /* Accessible target heights & focus rings */
        button, [data-testid="stLinkButton"] a {
            min-height: 2.65rem;
        }
        :is(button, a, input, textarea, [role="radiogroup"] label, [role="tab"]):focus-visible {
            outline: 3px solid #B84A24 !important;
            outline-offset: 2px;
        }
        /* Single Segmented Language Pill in Top Bar */
        [data-testid="stHorizontalBlock"]:has(.psi-crumb-pill) [role="radiogroup"][aria-orientation="horizontal"] {
            background: #EFF2F5;
            border: 1px solid #D9E0E6;
            border-radius: 0.65rem;
            padding: 0.2rem;
            gap: 0.25rem;
            justify-content: center;
            width: 100%;
        }
        [data-testid="stHorizontalBlock"]:has(.psi-crumb-pill) [role="radiogroup"][aria-orientation="horizontal"] label {
            flex: 1 1 0;
            justify-content: center;
            border-radius: 0.5rem;
            padding: 0.35rem 0.6rem;
            margin: 0 !important;
            min-height: 2.2rem;
            color: #0F1D2B;
            font-weight: 600;
            transition: background-color 0.15s ease, color 0.15s ease;
        }
        [data-testid="stHorizontalBlock"]:has(.psi-crumb-pill) [role="radiogroup"][aria-orientation="horizontal"] label:has(input:checked) {
            background: #0F1D2B !important;
            color: #FFFFFF !important;
        }
        [data-testid="stHorizontalBlock"]:has(.psi-crumb-pill) [role="radiogroup"][aria-orientation="horizontal"] label:has(input:checked) p {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        @media (max-width: 64rem) {
            [data-testid="stMainBlockContainer"] {
                padding-top: 2rem;
                padding-inline: 1rem;
            }
            .psi-hero-shell {
                grid-template-columns: 1fr;
            }
            [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"] {
                flex-wrap: wrap !important;
                gap: 0.75rem !important;
            }
            [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                flex: 1 1 16rem !important;
                width: auto !important;
                min-width: min(100%, 16rem) !important;
            }
        }
        @media (max-width: 48rem) {
            [data-testid="stSidebar"][aria-expanded="true"] {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                bottom: 0 !important;
                z-index: 999990 !important;
                max-width: min(20rem, 86vw) !important;
                box-shadow: 0.5rem 0 2rem rgba(15, 29, 43, 0.22) !important;
            }
            [data-testid="stMain"],
            [data-testid="stMainBlockContainer"] {
                flex: 1 1 100% !important;
                width: 100% !important;
                max-width: 100vw !important;
                min-width: 0 !important;
            }
        }
        @media (max-width: 40rem) {
            [data-testid="stMainBlockContainer"] {
                padding-top: 2.15rem;
                padding-inline: 0.85rem;
            }
            [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                flex: 1 1 100% !important;
                width: 100% !important;
                min-width: 100% !important;
            }
            .psi-entry-card-body {
                min-height: auto;
            }
            .psi-hero-shell {
                padding: 1rem;
            }
        }
        </style>"""
    )


def render_pillar_badge(label: str, *, key_hint: str | None = None) -> None:
    """Render an HTML-escaped semantic badge for Prevention, Detection, Suppression, or Context."""
    lookup = (key_hint or label).strip().casefold()
    bg, fg = _PILLAR_STYLES.get(lookup, ("#EFF2F5", "#3E4C59"))
    safe_label = html.escape(label, quote=True)
    st.markdown(
        f"<span class='psi-pillar-badge' style='background:{bg}; color:{fg};'>{safe_label}</span>",
        unsafe_allow_html=True,
    )


def render_hero_banner(kicker: str, summary: str, *, lang: str = "en") -> None:
    """Render an Aerospace Navy editorial hero banner with a crisp 1g vs 0g scientific diagram."""
    is_pt = str(lang).lower().startswith("pt")
    safe_kicker = html.escape(kicker, quote=True)
    safe_summary = html.escape(summary, quote=True)
    pill_1 = "RESUMIR" if is_pt else "SUMMARIZE"
    pill_2 = "RANQUEAR" if is_pt else "RANK"
    pill_3 = "INTERPRETAR" if is_pt else "INTERPRET"

    lbl_earth = "TERRA (1g)" if is_pt else "EARTH (1g)"
    lbl_earth_sub = "Chama em gota · Empuxo" if is_pt else "Teardrop flame · Buoyancy"
    lbl_space = "ÓRBITA (~0g)" if is_pt else "FREEFALL (~0g)"
    lbl_space_sub = "Chama esférica · Difusão" if is_pt else "Spherical flame · Diffusion"
    lbl_flow = "12 Estudos PSI · 40 Arquivos NASA → Busca Híbrida + Unidades" if is_pt else "12 NASA PSI Studies · 40 Verified Files → Hybrid RAG + Unit Guards"

    st.html(
        f"""
        <section class="psi-hero-shell" aria-label="Flame in Freefall visual overview">
          <div>
            <div class="psi-hero-kicker">{safe_kicker}</div>
            <p class="psi-hero-text">{safe_summary}</p>
            <div class="psi-hero-pills notranslate" translate="no">
              <span class="psi-hero-pill psi-hero-pill-flame">{pill_1}</span>
              <span class="psi-hero-pill">{pill_2}</span>
              <span class="psi-hero-pill">{pill_3}</span>
            </div>
          </div>
          <div class="psi-hero-diagram" role="img" aria-label="{html.escape(lbl_earth + ' vs ' + lbl_space, quote=True)}">
            <div class="psi-diag-grid">
              <div class="psi-diag-card">
                <div class="psi-diag-title">{html.escape(lbl_earth, quote=True)}</div>
                <div class="psi-diag-stage">
                  <span class="psi-diag-arrow" aria-hidden="true">↑</span>
                  <div class="psi-flame-1g-wrap">
                    <div class="psi-flame-1g"></div>
                    <div class="psi-fuel-base"></div>
                  </div>
                  <span class="psi-diag-arrow" aria-hidden="true">↑</span>
                </div>
                <div class="psi-diag-sub">{html.escape(lbl_earth_sub, quote=True)}</div>
              </div>
              <div class="psi-diag-card psi-diag-card-0g">
                <div class="psi-diag-title">{html.escape(lbl_space, quote=True)}</div>
                <div class="psi-diag-stage">
                  <span class="psi-diag-arrow" aria-hidden="true">→</span>
                  <div class="psi-flame-0g"></div>
                  <span class="psi-diag-arrow" aria-hidden="true">←</span>
                </div>
                <div class="psi-diag-sub">{html.escape(lbl_space_sub, quote=True)}</div>
              </div>
            </div>
            <div class="psi-diag-pipeline">{html.escape(lbl_flow, quote=True)}</div>
          </div>
        </section>
        """
    )


def render_context_navigation_bar(
    *,
    where_label: str,
    current_location: str,
    home_label: str,
    back_label: str,
    can_go_home: bool,
    on_go_home: Callable[[], None],
    on_go_back: Callable[[], None] | None,
    lang: str,
    on_lang_change: Callable[[], None],
    language_options: dict[str, str],
    language_label: str,
    active_journey_label: str | None = None,
    return_journey_label: str | None = None,
    on_return_journey: Callable[[], None] | None = None,
) -> None:
    """Render a consistent top breadcrumb, Back/Home navigation, and single EN/PT-BR selector."""
    with st.container(border=True):
        cols = st.columns([2.35, 0.9, 0.9, 1.5], vertical_alignment="center")
        loc_text = f"{where_label}: {current_location}"
        if active_journey_label:
            loc_text = f"{loc_text} · {active_journey_label}"
        cols[0].markdown(
            f"<span class='psi-crumb-pill notranslate' translate='no'>{html.escape(loc_text, quote=True)}</span>",
            unsafe_allow_html=True,
        )
        cols[1].button(
            back_label,
            key="topbar-back-btn",
            disabled=on_go_back is None,
            use_container_width=True,
            on_click=on_go_back if on_go_back is not None else (lambda: None),
        )
        cols[2].button(
            home_label,
            key="topbar-home-btn",
            disabled=not can_go_home,
            use_container_width=True,
            on_click=on_go_home,
        )
        with cols[3]:
            st.radio(
                language_label,
                options=list(language_options),
                format_func=lambda code: language_options[code],
                horizontal=True,
                label_visibility="collapsed",
                key="lang_selector",
                on_change=on_lang_change,
            )
        if return_journey_label and on_return_journey is not None:
            st.button(
                return_journey_label,
                type="primary",
                key="active-return-journey",
                on_click=on_return_journey,
            )


def render_five_question_framework(
    *,
    heading: str,
    q_labels: dict[str, str],
    exploring: str,
    why_matters: str,
    evidence_shows: str,
    conclusion: str,
    limitations: str,
) -> None:
    """Render the 5 beginner-friendly scientific questions cleanly for any journey step."""
    with st.container(border=True):
        st.subheader(heading)
        r1_c1, r1_c2 = st.columns(2, gap="medium")
        with r1_c1:
            st.markdown(f"**1. {q_labels['exploring']}**\n\n{exploring}")
        with r1_c2:
            st.markdown(f"**2. {q_labels['why_matters']}**\n\n{why_matters}")
        st.divider()
        r2_c1, r2_c2, r2_c3 = st.columns(3, gap="medium")
        with r2_c1:
            st.markdown(f"**3. {q_labels['evidence_shows']}**\n\n{evidence_shows}")
        with r2_c2:
            st.markdown(f"**4. {q_labels['conclusion']}**\n\n{conclusion}")
        with r2_c3:
            st.markdown(f"**5. {q_labels['limitations']}**\n\n{limitations}")


def style_scientific_figure(
    fig: go.Figure,
    *,
    title: str | None = None,
    height: int = 390,
) -> go.Figure:
    """Apply uniform aerospace-scientific typography, gridlines, margins, and palette to Plotly figures."""
    layout_kwargs: dict[str, Any] = {
        "template": "plotly_white",
        "colorway": PLOTLY_SCIDATA_COLORWAY,
        "height": height,
        "font": {"family": "Inter, Segoe UI, system-ui, sans-serif", "color": DESIGN_TOKENS["ink_primary"], "size": 12},
        "paper_bgcolor": "#FFFFFF",
        "plot_bgcolor": "#FFFFFF",
        "margin": {"l": 28, "r": 20, "t": 44 if title else 24, "b": 44},
        "legend": {"orientation": "h", "yanchor": "top", "y": -0.22, "xanchor": "left", "x": 0},
        "hovermode": "closest",
    }
    if title:
        layout_kwargs["title"] = {"text": title, "font": {"size": 15, "color": DESIGN_TOKENS["ink_primary"]}, "x": 0.01}
    fig.update_layout(**layout_kwargs)
    fig.update_xaxes(
        showgrid=True,
        gridcolor=DESIGN_TOKENS["gridline"],
        zeroline=False,
        linecolor=DESIGN_TOKENS["border_subtle"],
        tickfont={"color": DESIGN_TOKENS["ink_secondary"]},
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=DESIGN_TOKENS["gridline"],
        zeroline=False,
        linecolor=DESIGN_TOKENS["border_subtle"],
        tickfont={"color": DESIGN_TOKENS["ink_secondary"]},
    )
    return fig
