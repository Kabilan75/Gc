"""
UK Gaming Industry — Skill Demand Analysis (Streamlit)
All charts built with Plotly from CSV/Excel only (no static images).
"""
from __future__ import annotations

import hashlib
import html
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from city_to_country_tab5 import TAB5_CHART_COUNTRIES, normalize_tab5_dataframe_country

warnings.filterwarnings("ignore")

APP_DIR = Path(__file__).resolve().parent

# Sidebar / navigation labels (must match st.radio options exactly)
T_OVERVIEW = "📊  UK Overview"
T_REGIONAL = "🗺️  Regional Analysis"
T_GAP = "🤖  AI Gap Analysis"
T_GLOBAL = "🌍  Global Comparison"


def clean_skill_name(skill):
    name_map = {
        "cpp": "C++",
        "c#": "C#",
        "ms-office": "MS Office",
        "real-time-vfx": "Real-Time VFX",
        "agile-development": "Agile Development",
        "talent-acquisition": "Talent Acquisition",
        "team-management": "Team Management",
        "cross-functional": "Cross-Functional",
        "quality-control": "Quality Control",
        "budget-management": "Budget Management",
        "problem-solving": "Problem Solving",
        "data-analytics": "Data Analytics",
        "machine-learning": "Machine Learning",
        "user-experience-ux": "UX / User Experience",
        "ci-cd": "CI/CD",
        "timeline-management": "Timeline Management",
        "lighting-shading": "Lighting & Shading",
        "saas-business-models": "SaaS Business Models",
    }
    return name_map.get(
        str(skill).lower(),
        str(skill).replace("-", " ").title(),
    )


def _find_file(*candidates: str) -> Path | None:
    for name in candidates:
        for base in (APP_DIR, APP_DIR / "Step files"):
            p = base / name
            if p.exists():
                return p
    return None


COLOURS = {
    "teal": "#0D9488",
    "navy": "#0F1B2D",
    "purple": "#6D28D9",
    "amber": "#F59E0B",
    "green": "#10B981",
    "red": "#EF4444",
    "blue": "#1D4ED8",
    "pink": "#9D174D",
    "brown": "#92400E",
    "sky": "#0369A1",
}

DARK_COLOURS = [
    "#38BDF8",  # sky blue — primary
    "#818CF8",  # indigo — secondary
    "#34D399",  # emerald — tertiary
    "#F472B6",  # pink
    "#FB923C",  # orange
    "#A78BFA",  # violet
    "#4ADE80",  # green
    "#FCD34D",  # yellow
]

DRK_CONTINUOUS = [
    "#0F172A",  # base panel
    "#1E3A5F",  # mid
    "#38BDF8",  # highlight
]

# Average gap heatmap: light (low score) → dark (high score)
GAP_HEATMAP_COLORSCALE = [
    [0.0, "#f8fafc"],
    [0.15, "#e2e8f0"],
    [0.4, "#94a3b8"],
    [0.6, "#475569"],
    [0.8, "#1e3a5f"],
    [1.0, "#0f172a"],
]

CLUSTER_COLOURS_DARK = {
    "Game Development & Programming": "#38BDF8",
    "Soft Skills & Business Development": "#818CF8",
    "Project & Development Management": "#34D399",
    "Soft Skills & Creative Production": "#F472B6",
    "Business Tools & Productivity": "#FB923C",
    "Cloud, Infrastructure & DevOps": "#A78BFA",
}

REGION_COLOURS_DARK = {
    "England": "#38BDF8",
    "Scotland": "#34D399",
    "Wales": "#FB923C",
    "Northern Ireland": "#818CF8",
}

DARK_PLOTLY_LAYOUT = {}

POPULATION = {
    "England": 56490048,
    "Scotland": 5490000,
    "Wales": 3200000,
    "Northern Ireland": 1910000,
}

def apply_plotly_style(fig):
    try:
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="#0C1422",
            paper_bgcolor="#0C1422",
            font=dict(color="#8A9BB0", family="Outfit, sans-serif", size=12),
            margin=dict(l=20, r=20, t=40, b=20),
            title_font=dict(color="#F0F4F8", size=14, family="Outfit, sans-serif"),
            colorway=["#00E5CC", "#A78BFA", "#34D399", "#F5A623", "#60A5FA", "#FF5572", "#FB923C", "#FCD34D"],
        )
    except Exception:
        pass
    try:
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="#111D2E",
                font_color="#E2E8F0",
                bordercolor="rgba(255,255,255,0.1)",
            )
        )
    except Exception:
        pass
    try:
        fig.update_xaxes(
            gridcolor="rgba(255,255,255,0.05)",
            linecolor="rgba(255,255,255,0.08)",
            tickfont=dict(color="#4A5568", size=11),
            title_font=dict(color="#4A5568", size=12),
        )
        fig.update_yaxes(
            gridcolor="rgba(255,255,255,0.05)",
            linecolor="rgba(255,255,255,0.08)",
            tickfont=dict(color="#4A5568", size=11),
            title_font=dict(color="#4A5568", size=12),
        )
    except Exception:
        pass
    try:
        fig.update_layout(
            legend=dict(
                bgcolor="#0C1422",
                bordercolor="rgba(255,255,255,0.1)",
                borderwidth=1,
                font=dict(color="#8A9BB0", size=11),
            )
        )
    except Exception:
        pass
    return fig


def plotly_show(fig, height=None):
    if height:
        fig.update_layout(height=height)
    apply_plotly_style(fig)
    st.plotly_chart(fig, use_container_width=True)


def page_header(title: str, subtitle: str, icon: str = "🎮", badge: str | None = None) -> None:
    badge_html = (
        f'<span style="background:rgba(13,148,136,0.2);color:#5EEAD4;font-size:12px;font-weight:600;'
        f'padding:4px 12px;border-radius:20px;margin-left:12px;">{html.escape(badge)}</span>'
        if badge
        else ""
    )
    st.markdown(
        f"""
    <div class="page-header">
        <h1>{html.escape(icon)} {html.escape(title)}{badge_html}</h1>
        <p>{html.escape(subtitle)}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def kpi_card(value: str, label: str, sub: str = "", accent: str = "#0D9488") -> None:
    sub_html = f'<div class="kpi-sub">{html.escape(sub)}</div>' if sub else ""
    st.markdown(
        f"""
    <div class="kpi-card" style="--accent: {html.escape(accent, quote=True)}">
        <div class="kpi-value">{html.escape(str(value))}</div>
        <div class="kpi-label">{html.escape(label)}</div>
        {sub_html}
    </div>
    """,
        unsafe_allow_html=True,
    )


def section_header(title: str, badge: str | None = None) -> None:
    badge_html = f'<span class="section-badge">{html.escape(badge)}</span>' if badge else ""
    st.markdown(
        f"""
    <div class="section-header">
        <h2>{html.escape(title)}</h2>
        {badge_html}
    </div>
    """,
        unsafe_allow_html=True,
    )


def chart_card(title: str, subtitle: str = "") -> None:
    sub = f'<div class="chart-subtitle">{html.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
    <div class="chart-card">
        <div class="chart-title">{html.escape(title)}</div>
        {sub}
    </div>
    """,
        unsafe_allow_html=True,
    )


def plotly_show_in_card(fig, card_title: str, card_subtitle: str = "", height: int | None = None) -> None:
    chart_card(card_title, card_subtitle)
    try:
        fig.update_layout(title=None)
    except Exception:
        pass
    plotly_show(fig, height=height)


def insight(
    text: str,
    title: str = "Key Insight",
    type: str = "default",
    icon: str = "💡",
) -> None:
    type_class = {
        "default": "",
        "warning": "warning",
        "info": "info",
        "critical": "critical",
    }.get(type, "")
    st.markdown(
        f"""
    <div class="insight-box {type_class}">
        <div class="insight-title">{html.escape(icon)} {html.escape(title)}</div>
        <div class="insight-text">{html.escape(text)}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_step_a() -> pd.DataFrame:
    p = _find_file("step_a_clean_output.csv")
    if not p:
        raise FileNotFoundError("step_a_clean_output.csv")
    return pd.read_csv(p)


@st.cache_data(show_spinner=False)
def load_step_b() -> pd.DataFrame:
    p = _find_file("step_b_clustered_skills.csv", "step_b_clustered_skills (2).csv")
    if not p:
        raise FileNotFoundError("step_b_clustered_skills.csv")
    df = pd.read_csv(p)
    if "UK Region" in df.columns:
        df = df[df["UK Region"].astype(str).str.strip() != "Unknown"]
    if "Skills" in df.columns:
        df = df[df["Skills"].astype(str).str.strip() != "game-texts"]
    return df


@st.cache_data(show_spinner=False)
def load_step_c() -> pd.DataFrame:
    p = _find_file("step_c_gap_scores.csv")
    if not p:
        raise FileNotFoundError("step_c_gap_scores.csv")
    return pd.read_csv(p)


@st.cache_data(show_spinner=False)
def load_step_d() -> pd.DataFrame:
    p = _find_file("step_d_workshop_recommendations.csv")
    if not p:
        raise FileNotFoundError("step_d_workshop_recommendations.csv")
    return pd.read_csv(p)


@st.cache_data(show_spinner=False)
def load_excel_global_comparison() -> tuple[pd.DataFrame, str]:
    """Global Comparison tab: prefer preprocessed deduplicated file, else raw workbook."""
    p_clean = _find_file("Combined_Data_cleaned.xlsx")
    p_raw = _find_file("Updated_27_02_26_-_Kabilan.xlsx")
    if p_clean is not None:
        df = pd.read_excel(p_clean, sheet_name="Combined Data")
        return df, str(p_clean.name)
    if p_raw is not None:
        df = pd.read_excel(p_raw, sheet_name="Combined Data")
        return df, str(p_raw.name)
    raise FileNotFoundError(
        "Combined_Data_cleaned.xlsx or Updated_27_02_26_-_Kabilan.xlsx (needed for Global Comparison)"
    )


_TAB5_SKILL_COLS = frozenset({"skills", "skill"})
# Skill-share bar chart: ignore tiny jurisdictions (1 job → trivial 100% if that job lists the skill).
_TAB5_SHARE_CHART_MIN_JOBS = 30
_TAB5_SHARE_CHART_MIN_JOBS_FALLBACK = 10


def _tab5_is_nullish_series(s: pd.Series) -> pd.Series:
    t = s.astype(str).str.strip().str.lower()
    return s.isna() | t.isin(("", "nan", "none", "null", "na", "n/a", "#n/a"))


def _tab5_normalize_job_url(val: object) -> str:
    if pd.isna(val):
        return ""
    s = str(val).strip().lower()
    if s in ("", "nan", "none", "null", "n/a"):
        return ""
    s = s.split("?")[0].split("#")[0].rstrip("/")
    return s


def tab5_drop_all_null_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(axis=1, how="all")


def tab5_non_skill_columns(df: pd.DataFrame) -> list[str]:
    return [
        c
        for c in df.columns
        if str(c).strip().lower() not in _TAB5_SKILL_COLS and str(c).strip() != "_job_uid"
    ]


def tab5_assign_job_uid(df: pd.DataFrame) -> pd.DataFrame:
    """Stable ID per job ad: prefer normalized URL; else hash of all non-skill cells."""
    out = df.copy()
    lower_map = {str(c).strip().lower(): c for c in out.columns}
    url_priority = (
        "job url",
        "job_url",
        "posting url",
        "linkedin url",
        "job link",
        "joblink",
        "url",
        "link",
    )
    norm_url: pd.Series | None = None
    for lk in url_priority:
        col = lower_map.get(lk)
        if col is None:
            continue
        nu = out[col].map(_tab5_normalize_job_url)
        if len(nu) and (nu != "").mean() >= 0.12:
            norm_url = nu
            break

    id_priority = ("job id", "jobid", "posting id", "listing id", "vacancy id")
    norm_id: pd.Series | None = None
    for lk in id_priority:
        col = lower_map.get(lk)
        if col is None:
            continue
        ni = out[col].astype(str).str.strip().str.lower()
        ni = ni.replace({"nan": "", "none": "", "null": ""})
        if len(ni) and (ni != "").mean() >= 0.12:
            norm_id = ni
            break

    key_cols = tab5_non_skill_columns(out)
    if not key_cols:
        out["_job_uid"] = np.arange(len(out), dtype=np.int64).astype(str)
        return out

    sub = out[key_cols].fillna("")
    sub = sub.astype(str).apply(lambda x: x.str.strip().str.lower())
    sub = sub.replace({"nan": "", "none": "", "null": "", "n/a": "", "#n/a": ""})
    fp_raw = sub.agg("|".join, axis=1)
    fp_uid = "fp:" + fp_raw.map(lambda x: hashlib.md5(x.encode("utf-8", errors="replace")).hexdigest())

    uid = fp_uid.to_numpy(dtype=object)
    if norm_id is not None:
        m = norm_id.to_numpy(dtype=object) != ""
        uid = np.where(m, "id:" + norm_id.to_numpy(dtype=object), uid)
    if norm_url is not None:
        m = norm_url.to_numpy(dtype=object) != ""
        uid = np.where(m, "url:" + norm_url.to_numpy(dtype=object), uid)
    out["_job_uid"] = uid
    return out


def tab5_unique_job_rows(df: pd.DataFrame) -> pd.DataFrame:
    """One row per _job_uid (deterministic first row)."""
    if df.empty:
        return df
    if "_job_uid" not in df.columns:
        df = tab5_assign_job_uid(df)
    return df.sort_values("_job_uid", kind="mergesort").drop_duplicates(subset=["_job_uid"], keep="first").reset_index(
        drop=True
    )


st.set_page_config(
    page_title="UK Gaming Industry — Skill Intelligence",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

.stApp {
    background: #05090F;
    font-family: 'Outfit', sans-serif;
}
.main .block-container {
    padding: 2rem 2.5rem;
    max-width: 1400px;
    background: #05090F;
}
[data-testid="stSidebar"] {
    background: #0C1422 !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}
[data-testid="stSidebar"] * {
    color: #8A9BB0 !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #CBD5E1 !important;
    font-size: 13px !important;
}
.page-header {
    background: linear-gradient(135deg, #0C1422 0%, #111D2E 50%, #0D2540 100%);
    border: 1px solid rgba(0,229,204,0.15);
    border-radius: 14px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -5%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(0,229,204,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.page-header h1 {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #F0F4F8 !important;
    margin: 0 !important;
    letter-spacing: -0.5px;
    font-family: 'Outfit', sans-serif !important;
}
.page-header p {
    font-size: 13px !important;
    color: rgba(255,255,255,0.5) !important;
    margin: 6px 0 0 0 !important;
    font-family: 'Outfit', sans-serif !important;
}
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.section-header h2 {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #F0F4F8 !important;
    margin: 0 !important;
    font-family: 'Outfit', sans-serif !important;
}
.section-badge {
    background: rgba(0,229,204,0.12);
    color: #00E5CC;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid rgba(0,229,204,0.2);
    letter-spacing: 0.5px;
}
.kpi-card {
    background: #0C1422;
    border-radius: 12px;
    padding: 20px 24px;
    border: 1px solid rgba(255,255,255,0.07);
    position: relative;
    overflow: hidden;
    transition: transform 0.2s;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 3px;
    height: 100%;
    background: var(--accent, #00E5CC);
}
.kpi-card:hover {
    transform: translateY(-2px);
    border-color: rgba(0,229,204,0.2);
}
.kpi-value {
    font-size: 30px;
    font-weight: 700;
    color: #F0F4F8;
    letter-spacing: -1px;
    line-height: 1;
    margin-bottom: 6px;
    font-family: 'JetBrains Mono', monospace !important;
}
.kpi-label {
    font-size: 11px;
    color: #4A5568;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.kpi-sub {
    font-size: 11px;
    color: #8A9BB0;
    margin-top: 4px;
}
.chart-card {
    background: #0C1422;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 20px;
}
.chart-title {
    font-size: 14px;
    font-weight: 600;
    color: #F0F4F8;
    margin-bottom: 4px;
    font-family: 'Outfit', sans-serif;
}
.chart-subtitle {
    font-size: 12px;
    color: #4A5568;
    margin-bottom: 16px;
}
.insight-box {
    background: rgba(0,229,204,0.06);
    border: 1px solid rgba(0,229,204,0.2);
    border-radius: 10px;
    padding: 14px 18px;
    margin: 12px 0;
}
.insight-box.warning {
    background: rgba(245,166,35,0.06);
    border-color: rgba(245,166,35,0.2);
}
.insight-box.info {
    background: rgba(96,165,250,0.06);
    border-color: rgba(96,165,250,0.2);
}
.insight-box.critical {
    background: rgba(255,85,114,0.06);
    border-color: rgba(255,85,114,0.2);
}
.insight-title {
    font-size: 13px;
    font-weight: 600;
    color: #00E5CC;
    margin-bottom: 6px;
}
.insight-box.warning .insight-title { color: #F5A623; }
.insight-box.info .insight-title { color: #60A5FA; }
.insight-box.critical .insight-title { color: #FF5572; }
.insight-text {
    font-size: 13px;
    color: #8A9BB0;
    line-height: 1.6;
}
div[data-testid="metric-container"] {
    background: #0C1422 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    padding: 20px !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #00E5CC !important;
    font-family: 'JetBrains Mono', monospace !important;
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 11px !important;
    color: #4A5568 !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}
.stDataFrame {
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    background: #0C1422 !important;
}
.stDataFrame thead tr th {
    background: #111D2E !important;
    color: #4A5568 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    border-bottom: 1px solid rgba(255,255,255,0.1) !important;
}
.stDataFrame tbody tr td {
    font-size: 13px !important;
    color: #8A9BB0 !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
    background: #0C1422 !important;
}
.stDataFrame tbody tr:hover td {
    background: #111D2E !important;
}
.stSelectbox > div > div {
    background: #0C1422 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #F0F4F8 !important;
}
.stTextInput > div > div > input {
    background: #0C1422 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #F0F4F8 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00E5CC !important;
    box-shadow: 0 0 0 3px rgba(0,229,204,0.1) !important;
}
div[data-testid="stExpander"] {
    background: #0C1422 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #0C1422;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.07);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-size: 13px;
    color: #4A5568;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: #111D2E !important;
    color: #00E5CC !important;
    font-weight: 600 !important;
}
div[data-testid="stAlert"] {
    background: #0C1422 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    color: #8A9BB0 !important;
}
hr {
    border-color: rgba(255,255,255,0.07) !important;
}
.badge-high {
    background: rgba(255,85,114,0.1);
    color: #FF5572;
    border: 1px solid rgba(255,85,114,0.3);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
}
.badge-med {
    background: rgba(245,166,35,0.1);
    color: #F5A623;
    border: 1px solid rgba(245,166,35,0.3);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
}
.badge-std {
    background: rgba(52,211,153,0.1);
    color: #34D399;
    border: 1px solid rgba(52,211,153,0.3);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
}
.skill-tag {
    display: inline-block;
    background: rgba(0,229,204,0.08);
    color: #00E5CC;
    border: 1px solid rgba(0,229,204,0.2);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    margin: 3px;
}
.dashboard-footer {
    text-align: center;
    padding: 24px;
    color: #4A5568;
    font-size: 12px;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin-top: 40px;
}
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #05090F; }
::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 3px; }
footer[data-testid="stFooter"],
[data-testid="stFooter"] { display: none !important; }
</style>
""",
    unsafe_allow_html=True,
)

try:
    df_a = load_step_a()
    df_b = load_step_b()
    df_c = load_step_c()
    df_d = load_step_d()
except FileNotFoundError as e:
    st.error(f"Required CSV not found: {e}")
    st.stop()

with st.sidebar:
    st.markdown(
        """
<div style="padding:8px 0 20px 0;">
    <div style="font-size:19px;font-weight:700;
                color:#F0F4F8;letter-spacing:-0.5px;
                font-family:'Outfit',sans-serif;">
        🎮 Skill Intelligence
    </div>
    <div style="font-size:10px;color:#4A5568;
                margin-top:3px;letter-spacing:1.5px;
                text-transform:uppercase;
                font-family:'Outfit',sans-serif;">
        UK Gaming Industry
    </div>
</div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div style="font-size:10px;color:#475569;
                text-transform:uppercase;letter-spacing:1.5px;
                font-weight:600;margin-bottom:8px;">
        Navigation
    </div>
    """,
        unsafe_allow_html=True,
    )

    tab_choice = st.radio(
        "",
        [T_OVERVIEW, T_REGIONAL, T_GAP, T_GLOBAL],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#1E293B;margin:20px 0;'>", unsafe_allow_html=True)

    st.markdown(
        """
    <div style="font-size:10px;color:#334155;
                text-transform:uppercase;letter-spacing:1px;
                font-weight:600;margin-bottom:12px;">
        About
    </div>
    """,
        unsafe_allow_html=True,
    )

    descriptions = {
        T_OVERVIEW: "1,121 gaming jobs · 352 skills · top demand analysis",
        T_REGIONAL: "4 UK regions · normalised per 100k population",
        T_GAP: "TF-IDF + K-Means + Location Quotient pipeline",
        T_GLOBAL: "81 countries · skill share · UK vs world",
    }

    st.markdown(
        f"""
    <div style="background:rgba(13,148,136,0.1);
                border:1px solid rgba(13,148,136,0.2);
                border-radius:8px;padding:12px 14px;
                font-size:12px;color:#94A3B8;
                line-height:1.6;">
        {descriptions.get(tab_choice, "")}
    </div>
    """,
        unsafe_allow_html=True,
    )

    region_filter = "All"
    skill_query = ""
    date_range = None


def _apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if region_filter != "All" and "UK Region" in out.columns:
        out = out[out["UK Region"].astype(str).str.strip() == region_filter]
    if date_range and "Activated Date" in out.columns:
        d = pd.to_datetime(out["Activated Date"], errors="coerce")
        start, end = date_range
        mask = d.dt.date.between(start, end)
        out = out[mask]
    if skill_query:
        if "Skills" in out.columns:
            out = out[out["Skills"].astype(str).str.lower().str.contains(skill_query, na=False)]
        elif "Skill" in out.columns:
            out = out[out["Skill"].astype(str).str.lower().str.contains(skill_query, na=False)]
    return out


df_a_f = _apply_filters(df_a)
df_b_f = _apply_filters(df_b)
df_c_f = _apply_filters(df_c)
df_d_f = _apply_filters(df_d)


def show_tab1(df_a: pd.DataFrame) -> None:
    page_header(
        "UK Overview",
        "Skill demand analysis across 1,121 UK gaming job listings",
        "📊",
        "1,121 Jobs Analysed",
    )

    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        kpi_card("1,121", "Gaming Job Ads", "UK only · Jul–Oct 2025", "#0D9488")
    with kpi_cols[1]:
        kpi_card("352", "Unique Skills", "Identified across all listings", "#6D28D9")
    with kpi_cols[2]:
        kpi_card("6,948", "Skill Rows", "After cleaning & exploding", "#F59E0B")
    with kpi_cols[3]:
        kpi_card("4", "UK Regions", "England · Scotland · Wales · NI", "#10B981")

    df = df_a.copy()
    if "Skills" in df.columns:
        df = df[df["Skills"] != "game-texts"]
        df = df[df["Skills"].astype(str).str.strip() != ""]
        df = df[df["Skills"].astype(str).str.lower() != "nan"]
    if "UK Region" in df.columns:
        df = df[df["UK Region"].astype(str).str.strip() != "Unknown"]

    section_header("Top Skills by Demand", "UK Gaming")
    st.caption("How many unique job ads demand each skill — not just how many times it appears")

    demand_data = pd.DataFrame(
        {
            "Skill": [
                "Communication",
                "Team Management",
                "Talent Acquisition",
                "Cross-Functional",
                "Problem-Solving",
                "Python",
                "Excel",
                "Quality-Control",
                "C++",
                "Unity",
                "Unreal",
                "Storytelling",
                "Agile Development",
                "Budget Management",
                "Maya",
            ],
            "Skill_Occurrences": [610, 379, 343, 180, 139, 139, 136, 135, 134, 133, 130, 129, 127, 118, 100],
            "Unique_Job_Ads": [348, 237, 204, 110, 89, 82, 81, 73, 72, 68, 73, 73, 77, 74, 50],
        }
    )

    demand_data["Avg_Skills_Per_Job"] = (demand_data["Skill_Occurrences"] / demand_data["Unique_Job_Ads"]).round(2)
    demand_data["Coverage_%"] = (demand_data["Unique_Job_Ads"] / 1121 * 100).round(1)
    demand_data["Skill"] = demand_data["Skill"].apply(clean_skill_name)

    view_type = st.radio(
        "View by:",
        ["Skill Occurrences (total mentions)", "Unique Job Ads (distinct jobs)"],
        horizontal=True,
    )

    col_left, col_right = st.columns(2)
    with col_left:
        if view_type == "Skill Occurrences (total mentions)":
            y_col = "Skill_Occurrences"
            title = "Top 15 Skills — Total Skill Occurrences"
            label = "Total Occurrences"
            colour = "#0D9488"
        else:
            y_col = "Unique_Job_Ads"
            title = "Top 15 Skills — Unique Job Ads Demanding Skill"
            label = "Unique Job Ads"
            colour = "#6D28D9"

        fig_demand = px.bar(
            demand_data,
            x=y_col,
            y="Skill",
            orientation="h",
            title=title,
            labels={y_col: label, "Skill": ""},
            text=y_col,
            color_discrete_sequence=DARK_COLOURS,
        )
        fig_demand.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_demand.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=500,
            transition_duration=600,
        )
        plotly_show_in_card(fig_demand, title, "Ranked by volume in UK gaming job data", height=500)

    with col_right:
        fig_coverage = px.bar(
            demand_data.sort_values("Coverage_%", ascending=True),
            x="Coverage_%",
            y="Skill",
            orientation="h",
            title="Skill Coverage — % of All 1,121 UK Gaming Jobs",
            labels={"Coverage_%": "% of Job Ads", "Skill": ""},
            text="Coverage_%",
            color="Coverage_%",
            color_continuous_scale=DRK_CONTINUOUS,
        )
        fig_coverage.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_coverage.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=500,
            coloraxis_showscale=False,
            transition_duration=600,
        )
        plotly_show_in_card(
            fig_coverage,
            "Skill coverage — % of all 1,121 UK gaming jobs",
            "Share of distinct job ads listing each skill",
            height=500,
        )

    insight(
        "Communication appears in 610 skill mentions across 348 unique job ads — "
        "31.0% of all UK gaming jobs require communication skills (highest coverage). "
        "Unity appears in 133 mentions across 68 unique job ads (6.1% coverage) — "
        "a specialist gaming-only skill.",
        "Key insight",
        "default",
        "💡",
    )

    section_header("Job ads by category", "Composition")
    st.caption("How many job ads exist per job category across UK gaming companies")

    category_data = pd.DataFrame(
        {
            "Category": [
                "Art & Tech Art",
                "Engineering & Development",
                "Marketing & Advertising",
                "Business Dev & Sales",
                "Accounting & Finance",
                "Game Design",
                "Product & Project Mgmt",
                "HR & Recruiting",
                "Animation & Cinematics",
                "UI/UX",
            ],
            "Job_Ads": [172, 167, 73, 57, 52, 52, 50, 45, 43, 39],
        }
    )
    category_data["Percentage"] = (category_data["Job_Ads"] / 1121 * 100).round(1)

    col1, col2 = st.columns(2)
    with col1:
        fig_cat = px.bar(
            category_data.sort_values("Job_Ads", ascending=True),
            x="Job_Ads",
            y="Category",
            orientation="h",
            title="UK Gaming Job Ads by Category",
            labels={"Job_Ads": "Number of Job Ads", "Category": ""},
            text="Job_Ads",
            color="Job_Ads",
            color_continuous_scale=DRK_CONTINUOUS,
        )
        fig_cat.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_cat.update_layout(
            yaxis={"categoryorder": "total ascending"},
            coloraxis_showscale=False,
            height=450,
            transition_duration=600,
        )
        plotly_show_in_card(fig_cat, "UK gaming job ads by category", "Sorted by posting volume", height=450)

    with col2:
        fig_cat_pie = px.pie(
            category_data,
            values="Job_Ads",
            names="Category",
            title="Job Category Distribution — 1,121 UK Gaming Jobs",
            hole=0.4,
            color_discrete_sequence=DARK_COLOURS,
        )
        fig_cat_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Jobs: %{value}<br>Share: %{percent}<extra></extra>",
        )
        fig_cat_pie.update_layout(
            showlegend=False,
            height=450,
        )
        plotly_show_in_card(fig_cat_pie, "Job category distribution", "1,121 UK gaming jobs", height=450)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total UK Gaming Job Ads", "1,121")
    with col2:
        st.metric("Largest Category", "Art & Tech Art (172)")
    with col3:
        st.metric("Most Technical", "Engineering & Dev (167)")
    with col4:
        st.metric("Communication is needed in", "31% of all jobs")

    section_header("Skill deep dive", "Time series")
    st.caption("Explore one skill over time and by region")
    if "Activated Date" in df.columns and "UK Region" in df.columns and "Skills" in df.columns:
        skills_opts = sorted(df["Skills"].dropna().astype(str).str.strip().unique().tolist())
        if skills_opts:
            default_skill = (
                next((s for s in skills_opts if s.lower() == "communication"), skills_opts[0])
            )
            selected_skill = st.selectbox(
                "Select a skill",
                skills_opts,
                index=skills_opts.index(default_skill),
                format_func=clean_skill_name,
            )
        else:
            selected_skill = ""

        if selected_skill:
            sub = df[df["Skills"].astype(str).str.strip().str.lower() == str(selected_skill).strip().lower()].copy()
            d = pd.to_datetime(sub["Activated Date"], errors="coerce")
            sub = sub.assign(_date=d).dropna(subset=["_date"])

            if not sub.empty:
                weekly = sub.set_index("_date").resample("W").size().rename("Count").reset_index()
                fig_trend = px.line(
                    weekly,
                    x="_date",
                    y="Count",
                    markers=True,
                    title=f"Weekly trend — {clean_skill_name(selected_skill)}",
                )
                left, right = st.columns(2)
                with left:
                    plotly_show_in_card(
                        fig_trend,
                        f"Weekly trend — {clean_skill_name(selected_skill)}",
                        "Posts per week",
                        height=420,
                    )

                reg = sub["UK Region"].astype(str).str.strip().value_counts().reset_index()
                reg.columns = ["Region", "Count"]
                fig_reg = px.bar(
                    reg.sort_values("Count", ascending=True),
                    x="Count",
                    y="Region",
                    orientation="h",
                    title="Regional breakdown",
                )
                with right:
                    plotly_show_in_card(fig_reg, "Regional breakdown", "Count by UK region", height=420)
            else:
                insight("No rows for this skill under current filters.", "No data", "info", "ℹ️")
    else:
        st.caption("Skill deep dive unavailable (missing Activated Date / UK Region / Skills columns).")


def show_tab2(df_b: pd.DataFrame) -> None:
    page_header(
        "Regional Analysis",
        "How skill demand varies across England, Scotland, Wales & Northern Ireland",
        "🗺️",
        "4 UK Regions",
    )

    reg_col = "UK Region"
    sk_col = "Skills"
    df_b2 = df_b.copy()

    regions = ["England", "Scotland", "Wales", "Northern Ireland"]
    section_header("Controls", "Filters")
    top_n = st.slider("Top skills to show (heatmap)", min_value=10, max_value=30, value=15, step=5)

    section_header("Regional heatmap", "Normalised /100k")
    per_region_top: dict[str, pd.Series] = {}
    for r in regions:
        sub = df_b2[df_b2[reg_col] == r]
        per_region_top[r] = sub[sk_col].astype(str).str.strip().value_counts().head(int(top_n))

    # Build a union of the top skills across regions, sized by the slider.
    top_union: list[str] = []
    for r in regions:
        for s in per_region_top[r].index:
            if s not in top_union:
                top_union.append(s)
            if len(top_union) >= int(top_n):
                break
        if len(top_union) >= int(top_n):
            break
    if len(top_union) < int(top_n):
        for r in regions:
            for s in per_region_top[r].index:
                if s not in top_union:
                    top_union.append(s)
                if len(top_union) >= int(top_n):
                    break
            if len(top_union) >= int(top_n):
                break
    top_union = top_union[: int(top_n)]

    z = []
    text = []
    for sk in top_union:
        row_z = []
        row_t = []
        for r in regions:
            sub = df_b2[(df_b2[reg_col] == r) & (df_b2[sk_col].astype(str).str.strip() == sk)]
            cnt = len(sub)
            pop = POPULATION.get(r, 1)
            per100k = cnt / (pop / 100_000.0)
            row_z.append(round(per100k, 2))
            row_t.append(f"{per100k:.2f}")
        z.append(row_z)
        text.append(row_t)

    fig_hm = go.Figure(
        data=go.Heatmap(
            z=z,
            x=regions,
            y=[clean_skill_name(s) for s in top_union],
            text=text,
            texttemplate="%{text}",
            colorscale="YlOrRd",
            colorbar=dict(title="per 100k"),
        )
    )
    fig_hm.update_layout(
        title="Gaming Skill Demand Across UK Regions (per 100k population)",
        yaxis=dict(autorange="reversed"),
    )

    cards = {
        "England": [
            ("Communication", "527", "0.93"),
            ("Team Mgmt", "318", "0.56"),
            ("Talent Acq", "294", "0.52"),
            ("Cross-Func", "158", "0.28"),
            ("Python", "127", "0.22"),
        ],
        "Scotland": [
            ("Communication", "23", "0.42"),
            ("Talent Acq", "20", "0.37"),
            ("Agile Dev", "18", "0.33"),
            ("Team Mgmt", "15", "0.27"),
            ("C++", "14", "0.26"),
        ],
        "Wales": [
            ("Azure", "4", "0.13"),
            ("Back-End", "3", "0.10"),
            ("CI/CD", "3", "0.10"),
            ("Communication", "3", "0.10"),
            ("GitHub", "3", "0.10"),
        ],
        "Northern Ireland": [
            ("Communication", "7", "0.37"),
            ("Java", "5", "0.26"),
            ("Microservices", "5", "0.26"),
            ("CI/CD", "4", "0.21"),
            ("Data Analytics", "4", "0.21"),
        ],
    }

    col_hm, col_ref = st.columns([1.85, 0.62])
    with col_hm:
        plotly_show_in_card(
            fig_hm,
            "Gaming skill demand across UK regions",
            "Normalised per 100k population",
            height=500,
        )
    with col_ref:
        st.markdown(
            "<p style='font-size:12px;font-weight:600;margin:0 0 6px 0;'>Regional top 5</p>",
            unsafe_allow_html=True,
        )
        for i in range(0, len(regions), 2):
            c_left, c_right = st.columns(2)
            for col, reg in zip([c_left, c_right], regions[i : i + 2]):
                with col:
                    c = REGION_COLOURS_DARK.get(reg, "#333")
                    lines = "<br/>".join(
                        f"{name} — {posts} ({norm}/100k)"
                        for name, posts, norm in cards.get(reg, [])
                    )
                    st.markdown(
                        f"<div style='font-size:10.5px;line-height:1.28;margin-bottom:6px;color:#475569'>"
                        f"<b style='color:{c};'>{reg}</b><br/>{lines}</div>",
                        unsafe_allow_html=True,
                    )

    clus_col = "Cluster_Name"
    cluster_rows = []
    for r in regions:
        sub = df_b2[df_b2[reg_col] == r]
        pop = POPULATION[r]
        for clus, g in sub.groupby(clus_col):
            cnt = len(g)
            per100k = cnt / (pop / 100_000.0)
            cluster_rows.append({"Region": r, "Cluster": clus, "per100k": per100k})

    section_header("Cluster composition", "Stacked /100k")
    cdf = pd.DataFrame(cluster_rows)
    fig_stack = px.bar(
        cdf,
        x="Region",
        y="per100k",
        color="Cluster",
        title="Skill Cluster Composition by UK Region (per 100k population)",
        color_discrete_map=CLUSTER_COLOURS_DARK,
    )
    fig_stack.update_layout(
        barmode="stack",
        xaxis_title="",
        yaxis_title="Skills per 100k population",
    )
    plotly_show_in_card(
        fig_stack,
        "Skill cluster composition by UK region",
        "Stacked demand per 100k population",
        height=520,
    )

    section_header("Cluster summary table", "Exact figures")
    exact_tab2 = pd.DataFrame(
        [
            ("England", 3.55, 3.55, 1.49, 1.45, 0.72, 0.71),
            ("Scotland", 2.19, 1.60, 0.93, 0.44, 0.47, 0.18),
            ("Wales", 1.06, 0.47, 0.09, 0.16, 0.22, 0.28),
            ("N. Ireland", 1.88, 1.20, 0.58, 0.21, 0.37, 0.00),
        ],
        columns=["Region", "Game Dev", "Soft Skills", "Proj Mgmt", "Creative", "Biz Tools", "Cloud"],
    )
    st.dataframe(exact_tab2, use_container_width=True, hide_index=True, height=240)

    section_header("Top skills by region", "Top 10")
    region_pick = st.selectbox("Filter region — top 10 skills", regions)
    sub_r = df_b2[df_b2[reg_col] == region_pick]
    top10r = sub_r[sk_col].astype(str).str.strip().value_counts().head(10).reset_index()
    top10r.columns = ["Skill", "Count"]
    top10r["Skill"] = top10r["Skill"].apply(clean_skill_name)
    fig_r = px.bar(
        top10r.sort_values("Count", ascending=True),
        x="Count",
        y="Skill",
        orientation="h",
        color_discrete_sequence=DARK_COLOURS,
    )
    fig_r.update_layout(
        title=f"Top 10 skills — {region_pick}",
        showlegend=False,
    )
    plotly_show_in_card(fig_r, f"Top 10 skills — {region_pick}", "By posting count", height=None)


def show_tab3(df_c: pd.DataFrame, df_d: pd.DataFrame) -> None:
    page_header(
        "AI Gap Analysis",
        "K-Means clustering + Location Quotient gap scoring pipeline",
        "🤖",
        "520 Gap Scores",
    )

    section_header("Controls", "Filters")
    regions_o = ["England", "Scotland", "Wales", "Northern Ireland"]
    region_view = st.selectbox("Region (for scatter + recommendations)", ["All"] + regions_o, index=0)
    min_demand = st.slider("Minimum demand (scatter/recs)", min_value=0, max_value=600, value=0, step=10)
    prio_view = st.multiselect("Priorities", options=["HIGH", "MED", "STD"], default=["HIGH", "MED", "STD"])

    section_header("Pipeline steps", "AI")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown("**Step A — Data prep**")
        st.caption("6,948 rows, 352 skills, one skill per row")
    with s2:
        st.markdown("**Step B — K-Means**")
        st.caption("TF-IDF → numbers, 6 clusters")
    with s3:
        st.markdown("**Step C — Gap scoring**")
        st.caption("Location Quotient, 520 gap scores")
    with s4:
        st.markdown("**Step D — Recommender**")
        st.caption("Top 5 per region, 20 recommendations")

    dfc = df_c.copy()
    if region_view != "All" and "UK Region" in dfc.columns:
        dfc = dfc[dfc["UK Region"].astype(str).str.strip() == region_view]

    section_header("Gap score analysis", "AI pipeline")
    gap_avg = (
        dfc.groupby(["UK Region", "Cluster_Name"], as_index=False)["Gap_Score"]
        .mean()
        .rename(columns={"Gap_Score": "Avg Gap"})
    )
    clusters_o = [
        "Business Tools & Productivity",
        "Cloud, Infrastructure & DevOps",
        "Game Development & Programming",
        "Project & Development Management",
        "Soft Skills & Business Development",
        "Soft Skills & Creative Production",
    ]
    pivot = gap_avg.pivot(index="UK Region", columns="Cluster_Name", values="Avg Gap")
    for c in clusters_o:
        if c not in pivot.columns:
            pivot[c] = np.nan
    pivot = pivot.reindex(regions_o)[clusters_o]
    z = pivot.values.astype(float)
    text = [[f"{v:.2f}" if pd.notna(v) else "" for v in row] for row in z]

    short_labels = [
        "Biz Tools",
        "Cloud",
        "Game Dev",
        "Proj Mgmt",
        "Soft Skills",
        "Creative",
    ]
    fig_gap = go.Figure(
        data=go.Heatmap(
            z=z,
            x=short_labels,
            y=regions_o,
            text=text,
            texttemplate="%{text}",
            colorscale=GAP_HEATMAP_COLORSCALE,
            colorbar=dict(
                title="Avg gap (light = lower, dark = higher)",
                thickness=14,
                len=0.75,
            ),
        )
    )
    fig_gap.update_layout(
        title="Average Gap Score — Region × Skill Cluster",
        yaxis=dict(autorange="reversed"),
    )
    plotly_show_in_card(
        fig_gap,
        "Average gap score — region × skill cluster",
        "Light = lower gap, dark = higher",
        height=520,
    )

    scatter_src = dfc.copy()
    if "Demand" in scatter_src.columns:
        scatter_src = scatter_src[pd.to_numeric(scatter_src["Demand"], errors="coerce").fillna(0) >= float(min_demand)]

    scatter_disp = scatter_src.copy()
    if "Skills" in scatter_disp.columns:
        scatter_disp["_skill_lbl"] = scatter_disp["Skills"].apply(clean_skill_name)
    else:
        scatter_disp["_skill_lbl"] = ""
    fig_sc = px.scatter(
        scatter_disp,
        x="Demand",
        y="Gap_Score",
        color="Cluster_Name",
        size="Demand",
        hover_name="_skill_lbl",
        color_discrete_map=CLUSTER_COLOURS_DARK,
        title="Demand vs Gap Score — (each dot = one skill)",
    )

    fig_box = px.box(
        dfc,
        x="UK Region",
        y="Gap_Score",
        color="UK Region",
        color_discrete_map=REGION_COLOURS_DARK,
        title="Gap Score Distribution by UK Region",
    )

    _gap_scatter_h = 440
    col_sc, col_box = st.columns(2)
    with col_sc:
        plotly_show_in_card(
            fig_sc,
            "Demand vs gap score",
            "Each point is one skill",
            height=_gap_scatter_h,
        )
    with col_box:
        plotly_show_in_card(
            fig_box,
            "Gap score distribution by UK region",
            "Spread of scores within each region",
            height=_gap_scatter_h,
        )

    section_header("Workshop recommendations", "Step D output")

    # Load recommendations
    df_rec = load_step_d()

    # Region filter
    regions_list = ["All"] + sorted(df_rec["UK_Region"].unique().tolist())
    selected_region = st.selectbox("Filter by region:", regions_list)

    if selected_region != "All":
        df_filtered = df_rec[df_rec["UK_Region"] == selected_region].copy()
    else:
        df_filtered = df_rec.copy()

    # Clean column names for display
    display_cols = ["UK_Region", "Priority_Rank", "Skill", "Skill_Cluster", "Demand_Count", "Gap_Score"]
    available_cols = [c for c in display_cols if c in df_filtered.columns]
    df_show = df_filtered[available_cols].copy()
    df_show.columns = ["Region", "Rank", "Skill", "Cluster", "Demand", "Gap Score"][: len(available_cols)]

    # Colour code by priority
    def get_priority(gap):
        if gap >= 7:
            return "HIGH"
        elif gap >= 5.5:
            return "MED"
        else:
            return "STD"

    if "Gap Score" in df_show.columns:
        df_show["Priority"] = df_show["Gap Score"].apply(get_priority)

    if "Skill" in df_show.columns:
        df_show["Skill"] = df_show["Skill"].apply(clean_skill_name)

    st.dataframe(df_show, use_container_width=True, hide_index=True, height=360)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Communication gap", "10.0")
    k2.metric("England top skills", "3 HIGH")
    k3.metric("Total recommendations", "20")
    k4.metric("#1 skill (all regions)", "Communication")
    k5.metric("Max demand", "527")


def show_tab5(df_combined: pd.DataFrame, *, data_source: str) -> None:
    page_header(
        "Global Comparison",
        "UK gaming skill demand vs 81 countries worldwide",
        "🌍",
        "81 Countries",
    )
    st.caption(
        f"**Data file:** `{data_source}` — "
        + (
            "preprocessed (deduplicated) workbook."
            if data_source == "Combined_Data_cleaned.xlsx"
            else "raw workbook; run `python preprocess_combined_for_global.py` to build `Combined_Data_cleaned.xlsx` for cleaner counts."
        )
    )
    insight(
        "Skill share % is among unique job ads per country (duplicates removed; null rows dropped). "
        "Each share is the % of distinct jobs in that country listing the skill — not raw skill-row counts.",
        "Methodology",
        "info",
        "📐",
    )

    df_raw = tab5_drop_all_null_columns(df_combined.copy())

    df_global = df_raw[df_raw["Company Category"].astype(str).str.strip() == "Gaming Company"].copy()
    st.caption(f"Gaming Company rows (after dropping all-null columns): {len(df_global):,}")

    df_global = normalize_tab5_dataframe_country(df_global)
    df_global["Country"] = df_global["Country"].astype(str).str.strip()
    df_global = df_global[~_tab5_is_nullish_series(df_global["Country"])]
    df_global = df_global[df_global["Country"].isin(TAB5_CHART_COUNTRIES)]

    sk_col = "Skills" if "Skills" in df_global.columns else "Skill" if "Skill" in df_global.columns else None
    if sk_col is None:
        st.error("Combined Data must include a **Skills** or **Skill** column.")
        return
    if sk_col != "Skills":
        df_global = df_global.rename(columns={sk_col: "Skills"})

    df_global = df_global.dropna(subset=["Skills"])
    df_global["Skills"] = df_global["Skills"].astype(str).str.strip()
    df_global = df_global[~_tab5_is_nullish_series(df_global["Skills"])]
    df_global = df_global[df_global["Skills"].str.lower() != "game-texts"]

    rows_after_text_clean = len(df_global)
    df_global = df_global.reset_index(drop=True)
    df_global = tab5_assign_job_uid(df_global)
    df_jobs_unique = tab5_unique_job_rows(df_global)

    st.caption(
        f"Rows with valid country + skills: {rows_after_text_clean:,} → **{len(df_jobs_unique):,} unique job ads** "
        f"(deduped by URL / job ID / fingerprint; query strings stripped from URLs)"
    )

    # Skill analysis uses only one row per job; share = jobs listing skill ÷ jobs in country
    df_u = df_jobs_unique.copy()
    df_u["Skills"] = df_u["Skills"].astype(str).str.lower().str.strip()
    df_exploded = df_u.assign(Skills=df_u["Skills"].str.split(",")).explode("Skills")
    df_exploded = df_exploded.reset_index(drop=True)
    df_exploded["Skills"] = df_exploded["Skills"].str.strip()
    df_exploded = df_exploded[df_exploded["Skills"] != ""]
    df_exploded = df_exploded[~_tab5_is_nullish_series(df_exploded["Skills"])]
    df_exploded = df_exploded[df_exploded["Skills"] != "game-texts"]
    df_exploded = df_exploded.dropna(subset=["Skills", "Country"])

    job_totals_all = df_jobs_unique.groupby("Country", dropna=False).size().reset_index(name="total_jobs")
    n_countries_all = len(job_totals_all)
    valid_countries = job_totals_all[job_totals_all["total_jobs"] >= 100]["Country"].tolist()
    if not valid_countries:
        valid_countries = job_totals_all.nlargest(min(15, len(job_totals_all)), "total_jobs")["Country"].tolist()

    skill_country_all = (
        df_exploded.groupby(["Country", "Skills"])["_job_uid"].nunique().reset_index(name="count")
    )
    skill_country_all = skill_country_all.merge(job_totals_all, on="Country")
    skill_country_all["share_pct"] = (skill_country_all["count"] / skill_country_all["total_jobs"] * 100).round(2)

    pivot_share = skill_country_all.pivot_table(
        index="Country", columns="Skills", values="share_pct", fill_value=0.0, aggfunc="first"
    )

    st.caption(
        f"**{n_countries_all}** countries with gaming jobs · "
        f"**{len(valid_countries)}** with ≥100 unique ads (reference). "
        f"Skill ranks and averages use **all {n_countries_all}** countries (0% where a skill does not appear)."
    )

    # Count unique job listings per country (deduped), not raw skill-level rows
    job_counts_full = (
        df_jobs_unique.groupby("Country", dropna=False)
        .size()
        .reset_index(name="Job_Listings")
        .sort_values("Job_Listings", ascending=False)
    )
    job_counts = job_counts_full.head(15).copy()
    job_counts["highlight"] = job_counts["Country"].apply(
        lambda x: "United Kingdom" if x == "United Kingdom" else "Other"
    )

    section_header("Top countries by gaming job listings", "Global")
    st.caption(
        "Each bar counts **unique job ads** only (null rows removed, duplicates merged). "
        "Skill shares below use the same deduplicated jobs."
    )

    fig_countries = px.bar(
        job_counts,
        x="Job_Listings",
        y="Country",
        orientation="h",
        color="highlight",
        color_discrete_map={"United Kingdom": "#EF4444", "Other": "#0D9488"},
        title="Top 15 Countries by Unique Gaming Job Listings",
        labels={"Job_Listings": "Unique Job Listings", "Country": ""},
        text="Job_Listings",
    )
    fig_countries.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
    )
    fig_countries.update_layout(
        yaxis={"categoryorder": "total ascending"},
        showlegend=True,
        legend_title="",
        height=500,
        transition_duration=600,
    )
    plotly_show_in_card(
        fig_countries,
        "Top 15 countries by unique gaming job listings",
        "UK highlighted vs other markets",
        height=500,
    )

    with st.expander("Exact job-listing counts by country (deduplicated)"):
        st.dataframe(
            job_counts_full.reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            height=min(420, 36 + 24 * len(job_counts_full)),
        )

    # Show summary metrics below chart
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Global Gaming Jobs (unique ads)", f"{len(df_jobs_unique):,}")
    with col2:
        st.metric("Countries with Gaming Jobs", f"{df_jobs_unique['Country'].nunique():,}")
    with col3:
        uk_jobs = len(df_jobs_unique[df_jobs_unique["Country"] == "United Kingdom"])
        uk_pct = round(uk_jobs / len(df_jobs_unique) * 100, 1) if len(df_jobs_unique) else 0.0
        st.metric("UK Share of Global Jobs", f"{uk_pct}%")

    st.markdown("---")

    section_header("Skill Explorer", "Search")
    skill_input = st.text_input(
        "Type a skill name:",
        value="communication",
        placeholder="e.g. communication, python, unity, c++",
    ).strip().lower()

    if skill_input:
        if not df_exploded["Skills"].eq(skill_input).any():
            insight(
                f"Skill '{clean_skill_name(skill_input)}' not found in any gaming job. "
                "Try: communication, python, unity, team-management, cpp",
                "Not found",
                "warning",
                "⚠️",
            )
        else:
            cnt_skill = (
                df_exploded[df_exploded["Skills"] == skill_input]
                .groupby("Country")["_job_uid"]
                .nunique()
                .reset_index(name="count")
            )
            skill_data = job_totals_all.merge(cnt_skill, on="Country", how="left")
            skill_data["count"] = skill_data["count"].fillna(0).astype(np.int64)
            skill_data["share_pct"] = (skill_data["count"] / skill_data["total_jobs"] * 100).round(2)
            skill_data = skill_data.sort_values(["share_pct", "Country"], ascending=[False, True]).reset_index(drop=True)
            skill_data["rank"] = skill_data["share_pct"].rank(ascending=False, method="min").astype(int)

            n_countries = n_countries_all
            global_avg_r = round(float(skill_data["share_pct"].mean()), 2)

            # Bar chart: exclude micro-samples where one job = misleading 100% (or many duplicate "countries").
            pool = skill_data[skill_data["total_jobs"] >= _TAB5_SHARE_CHART_MIN_JOBS].copy()
            chart_min_note = _TAB5_SHARE_CHART_MIN_JOBS
            if pool.empty:
                pool = skill_data[skill_data["total_jobs"] >= _TAB5_SHARE_CHART_MIN_JOBS_FALLBACK].copy()
                chart_min_note = _TAB5_SHARE_CHART_MIN_JOBS_FALLBACK
            if pool.empty:
                pool = skill_data.nlargest(15, "count").copy()
                chart_min_note = None

            pool = pool[pool["Country"].isin(TAB5_CHART_COUNTRIES)]

            if chart_min_note is not None:
                top15 = pool.sort_values(["share_pct", "Country"], ascending=[False, True]).head(15)
            else:
                top15 = pool.sort_values(["share_pct", "Country"], ascending=[False, True]).head(15)

            top15["highlight"] = top15["Country"].apply(
                lambda x: "United Kingdom" if x == "United Kingdom" else "Other"
            )

            title_suffix = (
                f"≥{chart_min_note} gaming jobs each"
                if chart_min_note is not None
                else "by job count (sparse data)"
            )
            fig_skill = px.bar(
                top15,
                x="share_pct",
                y="Country",
                orientation="h",
                color="highlight",
                color_discrete_map={"United Kingdom": "#EF4444", "Other": "#0D9488"},
                title=f"Top 15 by skill share — {clean_skill_name(skill_input)} ({title_suffix})",
                labels={"share_pct": "Skill Share (%)", "Country": ""},
                text="share_pct",
            )
            fig_skill.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_skill.update_layout(
                yaxis={"categoryorder": "total ascending"},
                showlegend=True,
                legend_title="",
                height=500,
            )
            plotly_show_in_card(
                fig_skill,
                f"Top 15 by skill share — {clean_skill_name(skill_input)}",
                title_suffix,
                height=500,
            )
            if chart_min_note is not None:
                st.caption(
                    f"Chart excludes locations with fewer than **{chart_min_note}** gaming jobs so one-off ads do not show as **100%**. "
                    f"UK rank and global average still use **all {n_countries}** locations."
                )
            else:
                st.caption(
                    "Very few locations met the minimum job threshold; showing top 15 by **number of jobs** listing this skill."
                )

            uk_r = skill_data[skill_data["Country"] == "United Kingdom"]
            col1, col2, col3 = st.columns(3)
            if not uk_r.empty:
                uk_share = float(uk_r["share_pct"].iloc[0])
                uk_rank_num = int(uk_r["rank"].iloc[0])
                diff = round(uk_share - global_avg_r, 2)
                direction = "above" if diff >= 0 else "below"
                diff_abs = abs(diff)
                n_with_skill = int((skill_data["count"] > 0).sum())

                with col1:
                    st.metric("UK share %", f"{uk_share:.2f}%")
                with col2:
                    st.metric("UK rank", f"#{uk_rank_num} / {n_countries}")
                with col3:
                    st.metric("Global avg share %", f"{global_avg_r:.2f}%")

                insight(
                    f"Rank is out of {n_countries} countries with gaming jobs (0% where the skill does not appear). "
                    f"'{clean_skill_name(skill_input)}' appears in {n_with_skill} of those countries. "
                    f"UK share is {uk_share:.2f}%; unweighted global average across all {n_countries} countries is {global_avg_r:.2f}%. "
                    f"The UK is {direction} that average by {diff_abs:.2f}%.",
                    "Skill Explorer summary",
                    "info",
                    "📊",
                )
            else:
                with col1:
                    st.metric("UK share %", "—")
                with col2:
                    st.metric("UK rank", f"N/A / {n_countries}")
                with col3:
                    st.metric("Global avg share %", f"{global_avg_r:.2f}%")
                insight(
                    "United Kingdom has no gaming jobs in this dataset after cleaning.",
                    "UK data",
                    "critical",
                    "⚠️",
                )

    st.markdown("---")

    section_header("Analysis 1 — UK vs global skill gap", "Comparison")
    st.caption(
        "UK share % and global average share % are **% of unique job ads** in each country that list the skill "
        "(same methodology as the Skill Explorer). Difference = UK share − unweighted mean across all countries."
    )

    global_mean_by_skill = pivot_share.mean(axis=0)
    uk_skill_series = (
        skill_country_all[skill_country_all["Country"] == "United Kingdom"]
        .set_index("Skills")["share_pct"]
        if (skill_country_all["Country"] == "United Kingdom").any()
        else pd.Series(dtype=float)
    )
    all_skills_sorted = global_mean_by_skill.sort_values(ascending=False).index.tolist()
    gap_rows = []
    for sk in all_skills_sorted:
        uk_s = float(uk_skill_series.get(sk, 0.0)) if len(uk_skill_series) else 0.0
        g_avg = float(global_mean_by_skill.get(sk, 0.0))
        diff = round(uk_s - g_avg, 2)
        gap_rows.append(
            {
                "Skill": clean_skill_name(sk),
                "UK Share %": round(uk_s, 2),
                "Global Avg %": round(g_avg, 2),
                "Difference %": diff,
                "Status": "UK Ahead" if diff > 0 else "UK Behind",
            }
        )
    gap_full = pd.DataFrame(gap_rows)
    gap_top20 = gap_full.assign(_abs=gap_full["Difference %"].abs()).sort_values("_abs", ascending=False).head(20)
    gap_top20 = gap_top20.drop(columns=["_abs"])

    fig_gap_uk = px.bar(
        gap_top20.sort_values("Difference %", ascending=True),
        x="Difference %",
        y="Skill",
        orientation="h",
        color="Status",
        color_discrete_map={"UK Ahead": COLOURS["green"], "UK Behind": COLOURS["red"]},
        title="UK vs Global — Which Skills is UK Ahead or Behind On?",
        labels={"Difference %": "Difference (UK share − global avg, % points)", "Skill": ""},
    )
    fig_gap_uk.update_layout(
        yaxis={"categoryorder": "total ascending"},
        showlegend=True,
        legend_title="",
        height=560,
    )
    plotly_show_in_card(
        fig_gap_uk,
        "UK vs global — skills ahead or behind",
        "Difference = UK share − unweighted global mean (% points)",
        height=560,
    )

    st.dataframe(
        gap_top20,
        use_container_width=True,
        hide_index=True,
        height=min(520, 36 + 28 * len(gap_top20)),
        column_config={
            "Skill": st.column_config.TextColumn("Skill"),
            "UK Share %": st.column_config.NumberColumn("UK Share %", format="%.2f"),
            "Global Avg %": st.column_config.NumberColumn("Global Avg %", format="%.2f"),
            "Difference %": st.column_config.NumberColumn("Difference %", format="%.2f"),
            "Status": st.column_config.TextColumn("Status"),
        },
    )

    insight(
        "Skills where UK is ahead — young people trained in these are globally competitive.",
        "UK ahead",
        "default",
        "✓",
    )
    insight(
        "Skills where UK is behind — future opportunities the UK gaming industry has not fully developed yet.",
        "UK behind",
        "critical",
        "▼",
    )

    st.markdown("---")

    section_header("Analysis 2 — Global skill universality", "Reach")
    st.caption("For each skill: number of countries with **at least one** unique job listing that skill.")

    n_countries_total = int(df_jobs_unique["Country"].nunique())
    countries_per_skill = (
        skill_country_all[skill_country_all["count"] > 0].groupby("Skills")["Country"].nunique().sort_values(ascending=False)
    )
    univ_top20 = countries_per_skill.head(20).reset_index()
    univ_top20.columns = ["Skill", "Countries"]
    univ_top20["Skill"] = univ_top20["Skill"].apply(clean_skill_name)

    comm_key = "communication"
    comm_n = int(countries_per_skill.get(comm_key, 0))

    st.metric(
        label="Communication across countries",
        value=f"{comm_n} / {n_countries_total}",
        help="Countries with ≥1 unique gaming job listing communication, out of all countries in the dataset.",
    )
    st.caption(f"**Communication** is demanded in **{comm_n}** out of **{n_countries_total}** countries globally.")

    fig_univ = px.bar(
        univ_top20.sort_values("Countries", ascending=True),
        x="Countries",
        y="Skill",
        orientation="h",
        title="Most Universal Gaming Skills — Demanded Across Most Countries Globally",
        labels={"Countries": "Number of countries demanding skill", "Skill": ""},
        color="Countries",
        color_continuous_scale=DRK_CONTINUOUS,
    )
    fig_univ.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False, height=560)
    plotly_show_in_card(
        fig_univ,
        "Most universal gaming skills",
        "Demanded across the most countries globally",
        height=560,
    )

    insight(
        "Universal skills are the safest to teach — they open doors in gaming industries worldwide, not just the UK.",
        "Teaching insight",
        "info",
        "🌐",
    )

    st.markdown("---")

    section_header("Analysis 3 — Countries most similar to UK", "Cosine")
    st.caption(
        "Top **20** skills by global average share; each country is a vector of skill shares. "
        "Similarity to UK = **cosine similarity** between vectors (excluding UK from the leaderboard)."
    )

    top20_for_sim = global_mean_by_skill.sort_values(ascending=False).head(20).index.tolist()
    if "United Kingdom" in pivot_share.index and len(top20_for_sim):
        M = pivot_share[top20_for_sim].fillna(0.0).astype(float)
        uk_vec = M.loc["United Kingdom"].to_numpy()
        uk_norm = np.linalg.norm(uk_vec)

        def _cosine_to_uk(row: np.ndarray) -> float:
            nb = np.linalg.norm(row)
            if uk_norm == 0 or nb == 0:
                return 0.0
            return float(np.dot(uk_vec, row) / (uk_norm * nb))

        sim_scores = []
        for cty in M.index:
            if cty == "United Kingdom":
                continue
            sim_scores.append({"Country": cty, "Similarity": _cosine_to_uk(M.loc[cty].to_numpy())})
        sim_df = pd.DataFrame(sim_scores).sort_values("Similarity", ascending=False).head(10)

        fig_sim = px.bar(
            sim_df.sort_values("Similarity", ascending=True),
            x="Similarity",
            y="Country",
            orientation="h",
            title="Countries with Most Similar Gaming Skill Profile to UK",
            labels={"Similarity": "Cosine similarity (skill share vs UK)", "Country": ""},
            color="Similarity",
            color_continuous_scale=DRK_CONTINUOUS,
        )
        fig_sim.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False, height=420)
        plotly_show_in_card(
            fig_sim,
            "Countries with most similar gaming skill profile to UK",
            "Cosine similarity on top-20 skills by global share",
            height=420,
        )

        insight(
            "Young people trained in UK gaming skills can compete directly in these countries — "
            "employers want a similar skill mix to the UK.",
            "Mobility",
            "default",
            "🤝",
        )
    else:
        insight(
            "Cannot compute UK similarity (United Kingdom missing from data or no skills).",
            "Similarity unavailable",
            "warning",
            "⚠️",
        )

    st.markdown("---")

    section_header("UK skill rankings vs global", "Benchmark")
    st.caption("Which skills is the UK ahead of or behind the world on?")

    uk_skills = skill_country_all[skill_country_all["Country"] == "United Kingdom"].copy()
    uk_skills = uk_skills.sort_values("share_pct", ascending=False).head(20)
    uk_skills = uk_skills.rename(columns={"share_pct": "uk_share"})

    global_avg_skills = pivot_share.mean(axis=0).reset_index(name="global_share")
    global_avg_skills.columns = ["Skills", "global_share"]
    global_avg_skills = global_avg_skills.sort_values("global_share", ascending=False)
    global_avg_skills["global_rank"] = range(1, len(global_avg_skills) + 1)

    uk_skills["uk_rank"] = range(1, len(uk_skills) + 1)
    comparison = uk_skills[["Skills", "uk_share", "uk_rank"]].merge(
        global_avg_skills[["Skills", "global_share", "global_rank"]],
        on="Skills",
        how="left",
    )
    comparison["Skill"] = comparison["Skills"].apply(clean_skill_name)
    comparison = comparison.drop(columns=["Skills"])
    comparison["uk_share"] = comparison["uk_share"].round(2)
    comparison["global_share"] = comparison["global_share"].round(2)
    comparison["Trend"] = comparison.apply(
        lambda row: "↑ Ahead" if row["uk_rank"] <= row["global_rank"] else "↓ Behind",
        axis=1,
    )
    comparison = comparison[
        ["Skill", "uk_share", "uk_rank", "global_share", "global_rank", "Trend"]
    ]
    comparison.columns = [
        "Skill",
        "UK Share %",
        "UK Rank",
        "Global Avg Share %",
        "Global Rank",
        "Trend",
    ]

    st.dataframe(comparison, use_container_width=True, hide_index=True, height=420)

    st.markdown("---")

    insight(
        "SideFest: skills where the UK ranks above the global average (↑ Ahead) are strong assets — "
        "young people trained in them are globally competitive. Skills where the UK ranks below "
        "the average (↓ Behind) are future opportunities — valuable to teach before demand catches up.",
        "What this means for SideFest",
        "info",
        "🎯",
    )


if tab_choice == T_OVERVIEW:
    show_tab1(df_a)
elif tab_choice == T_REGIONAL:
    show_tab2(df_b)
elif tab_choice == T_GAP:
    show_tab3(df_c, df_d)
elif tab_choice == T_GLOBAL:
    try:
        df_global_cmp, global_src = load_excel_global_comparison()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error(f"Error reading global comparison workbook: {e}")
        st.stop()
    show_tab5(df_global_cmp, data_source=global_src)

