"""Centralized design tokens, accessible styling, navigation bar, and figure polish."""
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
        """<style>
        /* Prevent horizontal viewport overflow across desktop, tablet, and mobile */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            max-width: 100%;
            overflow-x: clip;
        }
        /* Layout clearance above fixed Streamlit top bar at 100% & 200% zoom */
        [data-testid="stMainBlockContainer"] {
            max-width: min(88rem, 100%);
            box-sizing: border-box;
            padding-top: 3.25rem;
            padding-bottom: 3.5rem;
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
        /* Hide developer Deploy button while preserving sidebar toggle control */
        [data-testid="stDeployButton"],
        [data-testid="stToolbarActions"] [data-testid="stDeployButton"] {
            display: none !important;
        }
        h1, h2, h3 {
            color: #0F1D2B;
            text-wrap: balance;
            letter-spacing: -0.02em;
        }
        .psi-lead {
            font-size: 1.06rem;
            color: #3E4C59;
            margin-top: -0.25rem;
            margin-bottom: 1.15rem;
            line-height: 1.58;
            max-width: 70ch;
        }
        .psi-hero {
            background: #FFFFFF;
            border: 1px solid #D9E0E6;
            border-left: 5px solid #B84A24;
            border-radius: 0.75rem;
            padding: 1.1rem 1.35rem;
            margin-bottom: 1rem;
        }
        .psi-hero-kicker {
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #1D5B86;
            margin-bottom: 0.25rem;
        }
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
            font-size: 0.86rem;
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
            padding: 0.85rem 1rem;
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
        /* Segmented pill look for sidebar horizontal Language radio */
        [data-testid="stSidebar"] [role="radiogroup"][aria-orientation="horizontal"] {
            background: #FFFFFF;
            border: 1px solid #D9E0E6;
            border-radius: 0.65rem;
            padding: 0.2rem;
            gap: 0.25rem;
        }
        [data-testid="stSidebar"] [role="radiogroup"][aria-orientation="horizontal"] label {
            border-radius: 0.5rem;
            padding: 0.25rem 0.5rem;
        }
        @media (max-width: 64rem) {
            [data-testid="stMainBlockContainer"] {
                padding-top: 3.5rem;
                padding-inline: 1rem;
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
                padding-top: 3.5rem;
                padding-inline: 0.85rem;
            }
            [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                flex: 1 1 100% !important;
                width: 100% !important;
                min-width: 100% !important;
            }
            .psi-hero {
                padding: 0.9rem 1rem;
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


def render_hero_banner(kicker: str, summary: str) -> None:
    """Render a clean editorial summary frame beneath a page heading."""
    safe_kicker = html.escape(kicker, quote=True)
    safe_summary = html.escape(summary, quote=True)
    st.markdown(
        f"<div class='psi-hero'>"
        f"<div class='psi-hero-kicker'>{safe_kicker}</div>"
        f"<div style='color:#0F1D2B; font-size:0.98rem; line-height:1.55;'>{safe_summary}</div>"
        f"</div>",
        unsafe_allow_html=True,
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
    on_toggle_lang: Callable[[], None],
    active_journey_label: str | None = None,
    return_journey_label: str | None = None,
    on_return_journey: Callable[[], None] | None = None,
) -> None:
    """Render a consistent top breadcrumb, Back/Home navigation, and quick EN/PT-BR pill."""
    with st.container(border=True):
        cols = st.columns([2.6, 1.0, 1.0, 1.25], vertical_alignment="center")
        loc_text = f"{where_label}: {current_location}"
        if active_journey_label:
            loc_text = f"{loc_text} · {active_journey_label}"
        cols[0].markdown(
            f"<span class='psi-crumb-pill'>{html.escape(loc_text, quote=True)}</span>",
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
        next_lang = "PT-BR" if lang == "en" else "EN"
        active_code = "EN" if lang == "en" else "PT-BR"
        cols[3].button(
            f"Language: {active_code} → {next_lang}",
            key="topbar-lang-toggle",
            use_container_width=True,
            on_click=on_toggle_lang,
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
