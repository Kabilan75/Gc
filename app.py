"""UK Gaming Industry — Skill Intelligence Dashboard (Streamlit)."""
from __future__ import annotations
import io
import shutil
import warnings
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")
APP_DIR = Path(__file__).resolve().parent

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UK Gaming — Skill Intelligence",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Host footer only (do not blanket-hide all <footer> — can break layout / accessibility).
st.html(
    """
<style id="gc-dash-hide-host-footer">
  [data-testid="stFooter"] { display: none !important; }
</style>
""".strip(),
)

# ── Minimal safe CSS  (only colours, no layout overrides) ─────────────────────
st.markdown("""
<style>
/* Sidebar above main so wide main pane never paints over sidebar text */
section[data-testid="stSidebar"] {
  background-color: #0C1422;
  position: relative;
  z-index: 100;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stRadio div { color: #CBD5E1 !important; }
.stApp { background-color: #05090F; color: #F0F4F8; }
.block-container { padding-top: 1rem; }
/*
 * Main pane only: extra top padding so first widgets (e.g. UK/Regional radio) sit below
 * Streamlit’s fixed header / deploy toolbar (avoids controls clipped under the black bar).
 */
section.main .block-container,
section[data-testid="stMain"] .block-container {
  max-width: 100% !important;
  padding-top: 3.75rem !important;
}
h1, h2, h3 { color: #F0F4F8 !important; }
p, li { color: #CBD5E1; }
[data-testid="stHorizontalBlock"] .stRadio label,
[data-testid="stHorizontalBlock"] .stRadio div { color: #CBD5E1 !important; }
/*
 * st.container(border=True) uses a wrapper that can sit above its children and
 * swallow clicks (radio, text inputs, Plotly toolbars). Let events pass through
 * the chrome only; keep widgets/charts interactive.
 */
div[data-testid="stVerticalBlockBorderWrapper"] {
    pointer-events: none !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] * {
    pointer-events: auto !important;
}
</style>
""", unsafe_allow_html=True)

# ── Colours ───────────────────────────────────────────────────────────────────
TEAL   = "#00E5CC"
S1     = "#0C1422"
S2     = "#111D2E"
PURPLE = "#A78BFA"
AMBER  = "#F5A623"
GREEN  = "#34D399"
RED    = "#FF5572"
BLUE   = "#60A5FA"
MUTED  = "#8A9BB0"
DIM    = "#4A5568"

CHART_COLS = [TEAL, PURPLE, GREEN, AMBER, BLUE, RED, "#FB923C", "#FCD34D"]
POP = {
    "England": 56_490_048, "Scotland": 5_490_000,
    "Wales": 3_200_000, "Northern Ireland": 1_910_000,
}

# ── Skill name map ────────────────────────────────────────────────────────────
_NM = {
    "cpp":"C++","c#":"C#","ms-office":"MS Office","real-time-vfx":"Real-Time VFX",
    "agile-development":"Agile Development","talent-acquisition":"Talent Acquisition",
    "team-management":"Team Management","cross-functional":"Cross-Functional",
    "quality-control":"Quality Control","budget-management":"Budget Management",
    "problem-solving":"Problem Solving","data-analytics":"Data Analytics",
    "machine-learning":"Machine Learning","user-experience-ux":"UX / User Experience",
    "ci-cd":"CI/CD","timeline-management":"Timeline Management",
    "back-end":"Back-End Dev","lighting-shading":"Lighting & Shading",
}
def cn(s):
    return _NM.get(str(s).lower(), str(s).replace("-", " ").title())

# ── Static datasets (aligned to uk_gaming_skill_intelligence_dashboard.html) ──
REG_HM_ROWS = ["England", "Scotland", "Wales", "N.Ireland"]
REG_HM_COLS = [
    "Communication",
    "Team Mgmt",
    "Talent Acq",
    "Cross-Func",
    "Python",
    "Quality Ctrl",
    "Storytelling",
    "Problem Solve",
    "Unity",
    "C++",
]
REG_HM_Z = [
    [0.93, 0.56, 0.52, 0.28, 0.22, 0.22, 0.21, 0.20, 0.19, 0.19],
    [0.42, 0.27, 0.36, 0.11, 0.07, 0.02, 0.04, 0.13, 0.22, 0.26],
    [0.09, 0.03, 0.03, 0.03, 0.06, 0.00, 0.00, 0.09, 0.00, 0.00],
    [0.37, 0.05, 0.10, 0.16, 0.05, 0.00, 0.00, 0.10, 0.00, 0.00],
]
CLUSTER_STACK_LABELS = ["England", "Scotland", "Wales", "N.Ireland"]
CLUSTER_STACK_SERIES = {
    "Game Dev": [3.55, 2.19, 1.06, 1.88],
    "Soft Skills": [3.55, 1.60, 0.93, 1.20],
    "Proj Mgmt": [1.49, 0.93, 0.09, 0.58],
    "Creative": [1.45, 0.44, 0.16, 0.21],
    "Biz Tools": [0.72, 0.47, 0.22, 0.37],
    "Cloud": [0.71, 0.18, 0.28, 0.00],
}
CLUSTER_STACK_COLS = ["#60A5FA", "#A78BFA", "#34D399", "#F472B6", "#F5A623", "#00E5CC"]
CAT_PIE_HTML = {
    "Soft Skills": 2499,
    "Other": 1457,
    "Tools": 893,
    "Programming": 639,
    "3D Art": 575,
    "Game Engines": 512,
    "Cloud": 373,
}
GAP_ENG_BARS = [
    ("Communication", 527, 10.0, TEAL),
    ("Team Management", 318, 7.99, PURPLE),
    ("Talent Acquisition", 294, 7.77, PURPLE),
    ("Cross-Functional", 158, 6.46, PURPLE),
    ("Python", 127, 6.16, BLUE),
    ("Unity", 122, 5.80, AMBER),
    ("C++", 121, 5.70, AMBER),
    ("Unreal", 130, 5.20, AMBER),
    ("Budget Mgmt", 118, 5.10, PURPLE),
    ("Maya", 100, 5.00, AMBER),
]
WORKSHOP_HTML = [
    ("England", "Communication", 527, "10.00", "HIGH"),
    ("England", "Team Management", 318, "7.99", "HIGH"),
    ("England", "Talent Acquisition", 294, "7.77", "HIGH"),
    ("England", "Cross-Functional", 158, "6.46", "MED"),
    ("England", "Python", 127, "6.16", "MED"),
    ("Scotland", "Communication", 23, "5.20", "STD"),
    ("Wales", "Azure", 4, "5.10", "STD"),
    ("N.Ireland", "Communication", 7, "5.00", "STD"),
]

# ── File finder ───────────────────────────────────────────────────────────────
def _find(*names):
    dirs = [APP_DIR, APP_DIR / "Step files", APP_DIR / "data"]
    for n in names:
        for d in dirs:
            p = Path(d) / n
            if p.exists():
                return p
        try:
            hits = list(APP_DIR.rglob(n))
            if hits:
                return hits[0]
        except Exception:
            pass
    return None

# ── Fallback hardcoded data ───────────────────────────────────────────────────
def _fallback_a():
    skill_data = [
        ("communication",560),("team-management",335),("talent-acquisition",317),
        ("cross-functional",168),("problem-solving",139),("python",139),
        ("excel",136),("quality-control",135),("cpp",134),("unity",133),
        ("unreal",130),("storytelling",129),("agile-development",127),
        ("budget-management",118),("maya",100),("c#",95),("ms-office",90),
        ("real-time-vfx",85),("data-analytics",78),("ci-cd",72),
    ]
    reg_split = {"England":0.82,"Scotland":0.09,"Wales":0.05,"Northern Ireland":0.04}
    rows = []
    for skill, total in skill_data:
        for region, frac in reg_split.items():
            for _ in range(max(1, int(total * frac))):
                rows.append({"Skills": skill, "UK Region": region})
    return pd.DataFrame(rows)

def _fallback_b():
    skill_cluster = {
        "communication":"Soft Skills & Business Development",
        "team-management":"Soft Skills & Business Development",
        "talent-acquisition":"Soft Skills & Business Development",
        "cross-functional":"Project & Development Management",
        "problem-solving":"Soft Skills & Creative Production",
        "python":"Cloud, Infrastructure & DevOps",
        "excel":"Business Tools & Productivity",
        "quality-control":"Project & Development Management",
        "cpp":"Game Development & Programming",
        "unity":"Game Development & Programming",
        "unreal":"Game Development & Programming",
        "storytelling":"Soft Skills & Creative Production",
        "agile-development":"Project & Development Management",
        "budget-management":"Business Tools & Productivity",
        "maya":"Soft Skills & Creative Production",
        "c#":"Game Development & Programming",
        "data-analytics":"Cloud, Infrastructure & DevOps",
        "aws":"Cloud, Infrastructure & DevOps",
        "azure":"Cloud, Infrastructure & DevOps",
        "ci-cd":"Cloud, Infrastructure & DevOps",
    }
    reg_split = {"England":0.82,"Scotland":0.09,"Wales":0.05,"Northern Ireland":0.04}
    rows = []
    for skill, cluster in skill_cluster.items():
        for region, frac in reg_split.items():
            for _ in range(max(1, int(20 * frac))):
                rows.append({"Skills": skill, "UK Region": region,
                             "Cluster_Name": cluster})
    return pd.DataFrame(rows)

def _fallback_c():
    skills = ["communication","team-management","talent-acquisition","cross-functional",
              "problem-solving","python","excel","quality-control","cpp","unity",
              "unreal","storytelling","agile-development","budget-management","maya",
              "c#","data-analytics","aws","azure","ci-cd"]
    demands = [527,318,294,158,139,127,136,124,121,122,
               130,129,127,118,100,95,78,60,55,50]
    region_gaps = {
        "England":        [10.0,7.99,7.77,6.46,6.16,6.10,5.90,5.80,5.70,5.60,
                           5.50,5.40,5.30,5.20,5.10,5.00,4.90,4.80,4.70,4.60],
        "Scotland":        [5.2,4.9,5.1,4.5,4.3,4.2,4.0,3.9,4.8,4.7,
                            4.6,4.5,5.0,4.4,4.3,4.2,4.1,4.0,3.9,3.8],
        "Wales":           [4.7,3.9,3.8,3.7,3.6,3.5,3.4,0.0,0.0,0.0,
                            0.0,0.0,3.8,3.7,3.6,3.5,3.4,3.3,3.2,3.1],
        "Northern Ireland":[5.0,4.5,4.4,4.3,4.2,4.1,4.0,0.0,4.8,0.0,
                            0.0,0.0,4.6,0.0,4.5,4.4,4.3,4.2,4.1,4.0],
    }
    cluster_map = {
        "communication":"Soft Skills & Business Development",
        "team-management":"Soft Skills & Business Development",
        "talent-acquisition":"Soft Skills & Business Development",
        "cross-functional":"Project & Development Management",
        "problem-solving":"Soft Skills & Creative Production",
        "python":"Cloud, Infrastructure & DevOps",
        "excel":"Business Tools & Productivity",
        "quality-control":"Project & Development Management",
        "cpp":"Game Development & Programming",
        "unity":"Game Development & Programming",
        "unreal":"Game Development & Programming",
        "storytelling":"Soft Skills & Creative Production",
        "agile-development":"Project & Development Management",
        "budget-management":"Business Tools & Productivity",
        "maya":"Soft Skills & Creative Production",
        "c#":"Game Development & Programming",
        "data-analytics":"Cloud, Infrastructure & DevOps",
        "aws":"Cloud, Infrastructure & DevOps",
        "azure":"Cloud, Infrastructure & DevOps",
        "ci-cd":"Cloud, Infrastructure & DevOps",
    }
    rows = []
    for region, gaps in region_gaps.items():
        for i, sk in enumerate(skills):
            rows.append({
                "UK Region": region, "Skills": sk,
                "Gap_Score": gaps[i], "Demand": demands[i],
                "Cluster_Name": cluster_map.get(sk, "Other"),
            })
    return pd.DataFrame(rows)

def _fallback_d():
    return pd.DataFrame([
        ["England","Communication","Soft Skills",527,10.00,"HIGH"],
        ["England","Team Management","Soft Skills",318,7.99,"HIGH"],
        ["England","Talent Acquisition","Soft Skills",294,7.77,"HIGH"],
        ["England","Cross-Functional","Proj Mgmt",158,6.46,"MED"],
        ["England","Python","Cloud/DevOps",127,6.16,"MED"],
        ["Scotland","Communication","Soft Skills",23,5.20,"STD"],
        ["Scotland","Talent Acquisition","Soft Skills",20,5.10,"STD"],
        ["Scotland","Agile Development","Proj Mgmt",18,5.00,"STD"],
        ["Scotland","Team Management","Soft Skills",15,4.90,"STD"],
        ["Scotland","C++","Game Dev",14,4.80,"STD"],
        ["Wales","Azure","Cloud/DevOps",4,5.10,"STD"],
        ["Wales","Back-End Dev","Game Dev",3,4.90,"STD"],
        ["Wales","CI/CD","Cloud/DevOps",3,4.80,"STD"],
        ["Wales","Communication","Soft Skills",3,4.70,"STD"],
        ["Wales","GitHub","Cloud/DevOps",3,4.60,"STD"],
        ["Northern Ireland","Communication","Soft Skills",7,5.00,"STD"],
        ["Northern Ireland","Java","Game Dev",5,4.80,"STD"],
        ["Northern Ireland","Microservices","Game Dev",5,4.70,"STD"],
        ["Northern Ireland","CI/CD","Cloud/DevOps",4,4.60,"STD"],
        ["Northern Ireland","Data Analytics","Cloud/DevOps",4,4.50,"STD"],
    ], columns=["UK Region","Skills","Cluster_Name","Demand","Gap_Score","Priority"])

# ── Data loaders (never crash) ────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_a():
    p = _find("step_a_clean_output.csv")
    if p:
        try:
            df = pd.read_csv(p)
            if "Skills" in df.columns:
                df = df[df["Skills"].astype(str).str.strip() != "game-texts"]
            if "UK Region" in df.columns:
                df = df[df["UK Region"].astype(str).str.strip() != "Unknown"]
            return df, True
        except Exception:
            pass
    return _fallback_a(), False

@st.cache_data(show_spinner=False)
def load_b():
    p = _find("step_b_clustered_skills.csv",
              "step_b_clustered_skills (2).csv")
    if p:
        try:
            df = pd.read_csv(p)
            if "UK Region" in df.columns:
                df = df[df["UK Region"].astype(str).str.strip() != "Unknown"]
            if "Skills" in df.columns:
                df = df[df["Skills"].astype(str).str.strip() != "game-texts"]
            return df, True
        except Exception:
            pass
    return _fallback_b(), False

@st.cache_data(show_spinner=False)
def load_c():
    p = _find("step_c_gap_scores.csv")
    if p:
        try:
            return pd.read_csv(p), True
        except Exception:
            pass
    return _fallback_c(), False

@st.cache_data(show_spinner=False)
def load_d():
    p = _find("step_d_workshop_recommendations.csv")
    if p:
        try:
            return pd.read_csv(p), True
        except Exception:
            pass
    return _fallback_d(), False


@st.cache_data(show_spinner=False)
def load_global_workbook() -> tuple[pd.DataFrame | None, str | None]:
    p = _find("Combined_Data_cleaned.xlsx", "Updated_27_02_26_-_Kabilan.xlsx")
    if not p:
        return None, None
    try:
        from city_to_country_tab5 import normalize_tab5_dataframe_country

        df = pd.read_excel(p, sheet_name="Combined Data", engine="openpyxl")
        df = normalize_tab5_dataframe_country(df)
        return df, p.name
    except Exception:
        return None, None


def _job_listing_count(df: pd.DataFrame) -> int:
    if df is None or df.empty or "Skills" not in df.columns:
        return 0
    cols = [c for c in df.columns if c != "Skills"]
    if not cols:
        return len(df)
    return int(df.drop_duplicates(subset=cols).shape[0])


def _cluster_counts_for_pie(df_b: pd.DataFrame) -> pd.Series:
    if df_b is None or df_b.empty or "Cluster_Name" not in df_b.columns:
        return pd.Series(dtype=float)
    return df_b["Cluster_Name"].astype(str).value_counts()


def _short_cluster(name: str) -> str:
    m = {
        "Game Development & Programming": "Game Dev",
        "Soft Skills & Business Development": "Soft Skills",
        "Project & Development Management": "Proj Mgmt",
        "Soft Skills & Creative Production": "Creative",
        "Business Tools & Productivity": "Biz Tools",
        "Cloud, Infrastructure & DevOps": "Cloud",
    }
    return m.get(name, name if len(name) <= 20 else name[:18] + "…")


def _reg_display(reg: str) -> str:
    if str(reg).strip() == "Northern Ireland":
        return "N. Ireland"
    return str(reg).strip()


def compute_regional_tables(
    df_a: pd.DataFrame,
) -> tuple[dict[str, list[tuple[str, int, float]]], list[list[float]], list[str], list[str]]:
    if df_a is None or df_a.empty or "Skills" not in df_a.columns:
        return {}, [], [], []
    regions = ["England", "Scotland", "Wales", "Northern Ireland"]
    top10 = df_a["Skills"].value_counts().head(10).index.tolist()
    xlabels = [cn(str(s)) for s in top10]
    ylabels = ["England", "Scotland", "Wales", "N.Ireland"]
    z: list[list[float]] = []
    regional: dict[str, list[tuple[str, int, float]]] = {}
    for reg in regions:
        sub = df_a[df_a["UK Region"].astype(str).str.strip() == reg]
        vc = sub["Skills"].value_counts().head(5)
        pop = float(POP.get(reg, 1))
        rows: list[tuple[str, int, float]] = []
        for sk, cnt in vc.items():
            p100 = float(cnt) / pop * 100_000
            rows.append((cn(str(sk)), int(cnt), round(p100, 2)))
        regional[_reg_display(reg)] = rows
        row = []
        for sk in top10:
            cnt = int((sub["Skills"] == sk).sum())
            row.append(cnt / pop * 100_000 if pop else 0.0)
        z.append(row)
    return regional, z, xlabels, ylabels


def compute_cluster_stack(df_b: pd.DataFrame) -> tuple[dict[str, list[float]], list[str]]:
    if df_b is None or df_b.empty or "Cluster_Name" not in df_b.columns:
        return {}, []
    regions = ["England", "Scotland", "Wales", "Northern Ireland"]
    sub = df_b[df_b["UK Region"].astype(str).str.strip().isin(regions)]
    if sub.empty:
        return {}, []
    ct = sub.groupby(["UK Region", "Cluster_Name"]).size().unstack(fill_value=0)
    cluster_order = [
        "Game Development & Programming",
        "Soft Skills & Business Development",
        "Project & Development Management",
        "Soft Skills & Creative Production",
        "Business Tools & Productivity",
        "Cloud, Infrastructure & DevOps",
    ]
    present = [c for c in cluster_order if c in ct.columns]
    x_labels = ["England", "Scotland", "Wales", "N.Ireland"]
    out: dict[str, list[float]] = {}
    for cname in present:
        sn = _short_cluster(cname)
        vals = []
        for reg in regions:
            pop = float(POP.get(reg, 1))
            v = float(ct.loc[reg, cname]) if reg in ct.index and cname in ct.columns else 0.0
            vals.append(v / pop * 100_000 if pop else 0.0)
        out[sn] = vals
    return out, x_labels


def _prior_from_rec(text: object) -> str:
    s = str(text)
    if "HIGH PRIORITY" in s:
        return "HIGH"
    if "MEDIUM" in s:
        return "MED"
    return "STD"


def gap_region_chart_df(df_c: pd.DataFrame, region: str, n: int = 12) -> pd.DataFrame:
    """Top-n skills in one UK region by gap score (Step C)."""
    out_cols = ["Skill", "Demand", "Gap"]
    if df_c is None or df_c.empty or not region:
        return pd.DataFrame(columns=out_cols)
    need = {"UK Region", "Skills", "Demand", "Gap_Score"}
    if not need.issubset(df_c.columns):
        return pd.DataFrame(columns=out_cols)
    r = str(region).strip()
    sub = df_c[df_c["UK Region"].astype(str).str.strip() == r].copy()
    if sub.empty:
        return pd.DataFrame(columns=out_cols)
    sub = sub.sort_values("Gap_Score", ascending=False).head(n)
    return pd.DataFrame(
        {
            "Skill": sub["Skills"].map(lambda s: cn(str(s))),
            "Demand": sub["Demand"].astype(int),
            "Gap": sub["Gap_Score"].astype(float),
        }
    )


def gap_cluster_heatmap(df_c: pd.DataFrame) -> tuple[list, list[str], list[str]]:
    if df_c is None or df_c.empty:
        return [], [], []
    g = df_c.groupby(["UK Region", "Cluster_Name"], as_index=False)["Gap_Score"].mean()
    pivot = g.pivot(index="UK Region", columns="Cluster_Name", values="Gap_Score")
    row_order = ["England", "Scotland", "Wales", "Northern Ireland"]
    rows = [r for r in row_order if r in pivot.index]
    if not rows:
        return [], [], []
    pivot = pivot.reindex(rows)
    cols = list(pivot.columns)
    z = pivot.fillna(0).values.tolist()
    y = [_reg_display(r) for r in rows]
    x = [_short_cluster(str(c)) for c in cols]
    return z, x, y


def _is_uk_country_mask(country_series: pd.Series) -> pd.Series:
    s = country_series.astype(str).str.strip().str.lower()
    return s.isin({"united kingdom", "uk", "u.k.", "gb", "great britain"})


def gaming_global_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    if "Company Category" not in df.columns:
        return df.copy()
    cc = df["Company Category"].astype(str).str.strip()
    return df.loc[cc == "Gaming Company"].copy()


def top_countries_jobs(gdf: pd.DataFrame) -> pd.Series:
    """Gaming job row counts per country (index = country name)."""
    if gdf is None or gdf.empty or "Country" not in gdf.columns:
        return pd.Series(dtype=int)
    s = gdf["Country"].astype(str).str.strip()
    s = s[s.str.len() > 0]
    return s.value_counts()


def explode_job_skills(gdf: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if gdf.empty or "Skills" not in gdf.columns:
        return pd.DataFrame(columns=["Country", "Skill"])
    for _, row in gdf.iterrows():
        c = str(row.get("Country", "")).strip()
        raw = row.get("Skills", "")
        if pd.isna(raw):
            continue
        for part in str(raw).split(","):
            sk = part.strip().lower()
            if sk and sk != "game-texts":
                rows.append({"Country": c, "Skill": sk})
    return pd.DataFrame(rows)


def skill_share_diffs(gdf: pd.DataFrame, top_n: int = 7) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    if gdf.empty or "Skills" not in gdf.columns:
        return [], []
    n_world = len(gdf)
    uk_mask = _is_uk_country_mask(gdf["Country"])
    uk = gdf.loc[uk_mask]
    n_uk = len(uk)
    if n_uk < 1:
        return [], []
    long_w = explode_job_skills(gdf)
    long_u = explode_job_skills(uk)
    if long_w.empty:
        return [], []
    world_rate = long_w.groupby("Skill").size() / n_world * 100
    uk_rate = long_u.groupby("Skill").size() / n_uk * 100
    common = world_rate.index.union(uk_rate.index)
    diffs: list[tuple[str, float]] = []
    for sk in common:
        wr = float(world_rate.get(sk, 0.0))
        ur = float(uk_rate.get(sk, 0.0))
        diffs.append((sk, ur - wr))
    diffs.sort(key=lambda x: x[1], reverse=True)
    ahead = [(cn(x[0]), round(x[1], 2)) for x in diffs if x[1] > 0.05][:top_n]
    behind_raw = sorted([x for x in diffs if x[1] < -0.05], key=lambda x: x[1])
    behind = [(cn(x[0]), round(-x[1], 2)) for x in behind_raw[:top_n]]
    return ahead, behind


# ── Plotly dark theme helper ──────────────────────────────────────────────────
def _dark(fig, h=None, *, margin_patch=None, axis_tick_color=None):
    tick = axis_tick_color if axis_tick_color is not None else DIM
    margin = dict(l=20, r=20, t=40, b=20)
    if margin_patch:
        margin.update(margin_patch)
    if h:
        fig.update_layout(height=h)
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=S1, paper_bgcolor=S1,
        font=dict(color=MUTED, size=12),
        margin=margin,
        title_font=dict(color="#F0F4F8", size=14),
        colorway=CHART_COLS,
        hoverlabel=dict(bgcolor=S2, font_color="#E2E8F0"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)",
                     linecolor="rgba(255,255,255,0.08)",
                     tickfont=dict(color=tick))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)",
                     linecolor="rgba(255,255,255,0.08)",
                     tickfont=dict(color=tick))
    return fig

def show(fig, h=None, *, margin_patch=None, axis_tick_color=None):
    st.plotly_chart(
        _dark(fig, h, margin_patch=margin_patch, axis_tick_color=axis_tick_color),
        use_container_width=True,
    )

# ── Load data ─────────────────────────────────────────────────────────────────
df_a, live_a = load_a()
df_b, live_b = load_b()
df_c, live_c = load_c()
df_d, live_d = load_d()
df_global, global_source_name = load_global_workbook()
all_live = live_a and live_b and live_c and live_d
live_steps = sum([live_a, live_b, live_c, live_d])

# ── Sidebar navigation (no footer attribution block) ─────────────────────────
NAV_OPTIONS = [
    "📊 UK & Regions",
    "🤖 AI Gap Analysis",
    "🌍 Global Comparison",
    "📄 CV Evaluator",
]
with st.sidebar:
    st.markdown("## 🎮 Skill Intelligence")
    st.markdown("**UK Gaming Industry**")
    st.markdown(
        """
<div style="font-size:10px;color:#475569;text-transform:uppercase;
letter-spacing:1.5px;font-weight:600;margin:12px 0 8px 0;">Navigation</div>
""",
        unsafe_allow_html=True,
    )
    tab = st.radio(
        "Section",
        NAV_OPTIONS,
        label_visibility="collapsed",
        key="main_nav_radio",
    )
    st.markdown("<hr style='border-color:#1E293B;margin:16px 0;'>", unsafe_allow_html=True)
    if all_live:
        st.success("📡 Live CSV data loaded")
    elif live_steps:
        st.warning(
            f"⚠️ Partial data — A={live_a} B={live_b} C={live_c} D={live_d}. "
            "Missing files use built-in demo tables."
        )
    else:
        st.info("📋 Demo mode — CSV files not found; charts use sample data")
    if global_source_name:
        st.caption(f"🌍 Global workbook: `{global_source_name}`")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — UK OVERVIEW + REGIONAL (sub-view switcher)
# ═════════════════════════════════════════════════════════════════════════════
if tab == "📊 UK & Regions":
    uk_sub = st.radio(
        "National vs regional",
        ["UK Overview", "Regional Analysis"],
        horizontal=True,
        label_visibility="visible",
        key="uk_regional_subview",
    )
    st.caption("Switch between national snapshot and per-region demand.")

    if uk_sub == "UK Overview":
        n_rows = len(df_a)
        n_jobs = _job_listing_count(df_a)
        n_skills = int(df_a["Skills"].nunique()) if "Skills" in df_a.columns else 0
        n_regions = (
            int(df_a["UK Region"].dropna().astype(str).str.strip().nunique())
            if "UK Region" in df_a.columns
            else 4
        )
        src = "Step A CSV" if live_a else "demo sample"
        vc15 = (
            df_a["Skills"].value_counts().head(15)
            if "Skills" in df_a.columns
            else pd.Series(dtype=int)
        )

        st.markdown(f"### UK Overview · `{n_jobs:,} listing groups`")
        st.caption(
            f"National snapshot · {n_jobs:,} unique listing rows (deduped on non-skill columns) · "
            f"{n_rows:,} skill mentions · source: {src}"
        )
        st.markdown("---")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Listing groups", f"{n_jobs:,}", "Deduped job rows in dataset")
        k2.metric("Unique Skills", f"{n_skills:,}", "Distinct skill tokens")
        k3.metric("Skill Rows", f"{n_rows:,}", "After cleaning in pipeline")
        k4.metric("UK Regions", str(n_regions), "ENG · SCO · WAL · NI")

        st.markdown("---")
        st.subheader("Top 15 skills by demand")
        st.caption(f"Occurrences in Step A — {n_rows:,} skill rows")
        col_ov_l, col_ov_r = st.columns(2)
        with col_ov_l:
            if len(vc15):
                df_top = pd.DataFrame({"Skill": [cn(str(s)) for s in vc15.index], "Count": vc15.values})
                fig_ov = px.bar(
                    df_top.sort_values("Count"),
                    x="Count",
                    y="Skill",
                    orientation="h",
                    title="Skill occurrences",
                    color_discrete_sequence=[TEAL],
                )
                fig_ov.update_layout(showlegend=False, yaxis_categoryorder="total ascending")
                fig_ov.update_traces(texttemplate="%{x:,}", textposition="outside")
                show(fig_ov, 460)
            else:
                st.warning("No skills in the current dataset.")
        with col_ov_r:
            pie_series = _cluster_counts_for_pie(df_b)
            if pie_series.empty:
                pie_series = pd.Series(CAT_PIE_HTML)
            fig_pie = px.pie(
                values=pie_series.values,
                names=[_short_cluster(str(x)) for x in pie_series.index],
                hole=0.58,
                title="Rows by AI cluster (Step B)",
                color_discrete_sequence=[TEAL, DIM, BLUE, PURPLE, AMBER, GREEN, RED],
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(showlegend=True, legend=dict(font=dict(size=11)))
            show(fig_pie, 320)
            if len(pie_series) > 0:
                i_max = int(pie_series.values.argmax())
                big = _short_cluster(str(pie_series.index[i_max]))
                st.caption(
                    f"{'Step B CSV — ' if live_b else 'Demo / fallback — '}"
                    f"{int(pie_series.sum())} clustered skill rows · **{big}** largest segment"
                )
            else:
                st.caption("No cluster data")

        st.markdown("---")
        st.subheader("Top 10 skills — share of demand")
        st.caption("Gaming dataset (Step A); % = share of all skill mentions in this file")
        if "Skills" in df_a.columns and n_rows > 0:
            t10 = df_a["Skills"].value_counts().head(10)
            hier = pd.DataFrame(
                {
                    "Skill": [cn(str(s)) for s in t10.index],
                    "Occurrences": t10.values.astype(int),
                    "% of rows": [round(100 * int(c) / n_rows, 1) for c in t10.values],
                }
            )
        else:
            hier = pd.DataFrame(columns=["Skill", "Occurrences", "% of rows"])
        st.dataframe(hier, use_container_width=True, hide_index=True)

    else:
        regional, z_hm, x_hm, y_hm = compute_regional_tables(df_a)
        stack_dict, stack_x = compute_cluster_stack(df_b)

        if not regional:
            regional = {
                "England": [("—", 0, 0.0)],
                "Scotland": [("—", 0, 0.0)],
                "Wales": [("—", 0, 0.0)],
                "N. Ireland": [("—", 0, 0.0)],
            }
        eng = regional.get("England", [("—", 0, 0.0)])[0]
        scot_cpp = next(
            ((s, p) for s, _c, p in regional.get("Scotland", []) if "c++" in s.lower()),
            None,
        )
        if not scot_cpp and regional.get("Scotland"):
            scot_cpp = (regional["Scotland"][0][0], regional["Scotland"][0][2])
        wales_unity = 0.0
        if z_hm and x_hm:
            wi = next((i for i, lab in enumerate(x_hm) if "unity" in lab.lower()), None)
            if wi is not None and len(z_hm) > 2:
                wales_unity = z_hm[2][wi]
        ni_cloud = float(stack_dict.get("Cloud", [0.0, 0.0, 0.0, 0.0])[-1]) if stack_dict else 0.0

        st.markdown("### Regional Analysis · `4 Regions`")
        st.caption(
            "England · Scotland · Wales · Northern Ireland — normalised per 100k population "
            f"(Step A rows · clusters from Step B)"
        )
        st.markdown("---")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("England /100k", f"{eng[2]:.2f}", str(eng[0]))
        c2.metric("Scotland /100k", f"{scot_cpp[1]:.2f}" if scot_cpp else "0.00", scot_cpp[0] if scot_cpp else "Top skill")
        c3.metric("Wales Unity /100k", f"{wales_unity:.2f}", "From heatmap column")
        c4.metric("NI Cloud /100k", f"{ni_cloud:.2f}", "Cluster stack (Step B)")

        st.markdown("---")
        st.subheader("Top 5 skills per region")
        st.caption("Count · per 100k")
        cols4 = st.columns(4)
        for i, reg in enumerate(["England", "Scotland", "Wales", "N. Ireland"]):
            with cols4[i]:
                st.subheader(reg)
                skills = regional.get(reg, [])
                rows = [{"Skill": s, "Count": c, "/100k": p} for s, c, p in skills]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.subheader("Skill demand heatmap")
        st.caption("Per 100k population · Top 10 skills × 4 regions (Step A)")
        if z_hm and x_hm and y_hm:
            hm_t = [[f"{v:.2f}" for v in row] for row in z_hm]
            fig_hm = go.Figure(
                go.Heatmap(
                    z=z_hm,
                    x=x_hm,
                    y=y_hm,
                    text=hm_t,
                    texttemplate="%{text}",
                    colorscale=[[0, S2], [0.35, "#0D5A7A"], [1, TEAL]],
                    hovertemplate="<b>%{y}</b> · %{x}<br>%{z:.2f} /100k<extra></extra>",
                )
            )
        else:
            hm_t = [[f"{v:.2f}" for v in row] for row in REG_HM_Z]
            fig_hm = go.Figure(
                go.Heatmap(
                    z=REG_HM_Z,
                    x=REG_HM_COLS,
                    y=REG_HM_ROWS,
                    text=hm_t,
                    texttemplate="%{text}",
                    colorscale=[[0, S2], [0.35, "#0D5A7A"], [1, TEAL]],
                    hovertemplate="<b>%{y}</b> · %{x}<br>%{z:.2f} /100k<extra></extra>",
                )
            )
        fig_hm.update_layout(title="Top 10 skills × 4 regions", yaxis=dict(autorange="reversed"))
        show(fig_hm, 420)
        st.caption("Darker teal = higher demand per 100k population")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI GAP ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "🤖 AI Gap Analysis":
    n_gap = len(df_c)
    n_rec = len(df_d)
    n_a_rows = len(df_a)
    n_a_skills = int(df_a["Skills"].nunique()) if "Skills" in df_a.columns else 0
    n_cl = int(df_c["Cluster_Name"].nunique()) if live_c and "Cluster_Name" in df_c.columns else 6

    st.markdown(f"### AI Gap Analysis · `{n_gap} gap rows`")
    st.caption(
        "TF-IDF · K-Means clustering · Location Quotient gap scoring · Workshop recommender "
        f"(Step C: {n_gap} rows · Step D: {n_rec} recommendations)"
    )
    st.markdown("---")

    st.subheader("The AI pipeline")
    st.caption("Step A → B → C → D")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown(f"**A · Data Prep**\n\n{n_a_rows:,} rows · {n_a_skills} skills")
    with p2:
        st.markdown("**B · K-Means AI**\n\nTF-IDF · 6 clusters")
    with p3:
        st.markdown(f"**C · Gap Scoring**\n\nLoc. Quotient · {n_gap}")
    with p4:
        st.markdown(f"**D · Recommender**\n\nTop picks · {n_rec} rows")

    st.markdown("---")
    st.subheader("Cluster composition")
    st.caption(
        "Per 100k population · K-Means grouping (Step B) · six AI cluster stacks per UK region"
    )
    stack_mix, stack_regions = compute_cluster_stack(df_b)
    fig_cl = go.Figure()
    if stack_mix and stack_regions:
        for i, (name, vals) in enumerate(stack_mix.items()):
            fig_cl.add_trace(
                go.Bar(
                    name=name,
                    x=stack_regions,
                    y=vals,
                    marker_color=CLUSTER_STACK_COLS[i % len(CLUSTER_STACK_COLS)],
                    marker_line_width=0,
                )
            )
    else:
        for i, (name, vals) in enumerate(CLUSTER_STACK_SERIES.items()):
            fig_cl.add_trace(
                go.Bar(
                    name=name,
                    x=CLUSTER_STACK_LABELS,
                    y=vals,
                    marker_color=CLUSTER_STACK_COLS[i],
                    marker_line_width=0,
                )
            )
    fig_cl.update_layout(
        barmode="stack",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.28,
            x=0.5,
            xanchor="center",
            font=dict(size=11),
        ),
        xaxis_title="Region",
        yaxis_title="Per 100k",
    )
    show(fig_cl, 440, margin_patch=dict(t=12, b=120), axis_tick_color="#CBD5E1")
    st.caption("Game Dev · Soft Skills · Proj Mgmt · Creative · Biz Tools · Cloud")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    z_gh, x_gh, y_gh = gap_cluster_heatmap(df_c)
    if not z_gh:
        gv = {
            "England": [5.07, 5.09, 5.09, 5.21, 5.26, 5.09],
            "Scotland": [4.74, 4.25, 4.62, 4.82, 4.75, 4.82],
            "Wales": [3.41, 3.50, 3.59, 4.18, 4.64, 4.66],
            "N.Ireland": [2.77, 0.00, 3.90, 4.63, 4.52, 4.69],
        }
        gcl = ["Biz Tools", "Cloud", "Game Dev", "Proj Mgmt", "Soft Skills", "Creative"]
        z_g = [[gv[r][i] for i in range(6)] for r in gv]
        x_gh, y_gh, z_gh = gcl, list(gv.keys()), z_g

    ni_cloud_zero = False
    if y_gh and x_gh and z_gh:
        for yi, row in zip(y_gh, z_gh):
            yl = str(yi).lower()
            if "ireland" in yl and "n." in yl:
                for xi, val in zip(x_gh, row):
                    if str(xi).lower() == "cloud" and abs(float(val)) < 1e-9:
                        ni_cloud_zero = True
    eng_row = next(
        (r for r, y in zip(z_gh, y_gh) if str(y).lower().startswith("england")),
        None,
    )
    eng_rng = ""
    if eng_row:
        lo, hi = min(eng_row), max(eng_row)
        eng_rng = f"England gap range **{lo:.2f}–{hi:.2f}** (mean by cluster)."

    with col_l:
        st.caption("Average gap score — region × cluster")
        st.caption("Location Quotient · darker = more urgent · 0.00 = zero demand")
        fig_ghm = go.Figure(
            go.Heatmap(
                z=z_gh,
                x=x_gh,
                y=y_gh,
                text=[[f"{float(v):.2f}" for v in row] for row in z_gh],
                texttemplate="%{text}",
                colorscale=[[0, S2], [0.35, "#0D2540"], [1, TEAL]],
                hovertemplate="<b>%{y} — %{x}</b><br>Gap: %{z:.2f}<extra></extra>",
            )
        )
        fig_ghm.update_layout(title="Region × cluster gap scores", yaxis=dict(autorange="reversed"))
        show(fig_ghm, 340)
        if ni_cloud_zero:
            st.warning(
                "⚠️ **N. Ireland Cloud ≈ 0** — Little or no Cloud cluster demand in the Step C matrix. "
                + (eng_rng or "")
            )
        elif eng_rng:
            st.info(eng_rng)

    with col_r:
        st.caption("Workshop recommendations")
        st.caption("Step D output — ranked by gap score · priority coded")
        _d_cols = {"UK_Region", "Skill", "Demand_Count", "Gap_Score"}
        if not df_d.empty and _d_cols.issubset(df_d.columns):
            ws_df = pd.DataFrame(
                {
                    "Region": df_d["UK_Region"],
                    "Skill": df_d["Skill"],
                    "Demand": df_d["Demand_Count"].astype(int),
                    "Gap": df_d["Gap_Score"].map(lambda x: f"{float(x):.2f}"),
                    "Priority": df_d["Workshop_Recommendation"].map(_prior_from_rec)
                    if "Workshop_Recommendation" in df_d.columns
                    else "—",
                }
            )
        else:
            ws_df = pd.DataFrame(
                WORKSHOP_HTML,
                columns=["Region", "Skill", "Demand", "Gap", "Priority"],
            )
        st.dataframe(ws_df, use_container_width=True, hide_index=True)

    st.subheader("Demand vs gap score — by region")
    _gap_regions = ["England", "Scotland", "Wales", "Northern Ireland"]
    _present = _gap_regions
    if len(df_c) and "UK Region" in df_c.columns:
        have = set(df_c["UK Region"].astype(str).str.strip().unique())
        _present = [x for x in _gap_regions if x in have] or _gap_regions
    gap_pick = st.selectbox(
        "UK region",
        _present,
        index=0,
        key="gap_demand_region_select",
        help="Step C gap scores and demand per skill for the chosen region.",
    )
    st.caption(f"Each row = one skill in **{gap_pick}** (Step C) · gap score out of 10")
    df_reg_gap = gap_region_chart_df(df_c, gap_pick, n=12)
    used_fallback = False
    if df_reg_gap.empty and gap_pick == "England":
        df_reg_gap = pd.DataFrame(
            [(a, b, c) for a, b, c, _ in GAP_ENG_BARS], columns=["Skill", "Demand", "Gap"]
        )
        used_fallback = True
    df_reg_gap = df_reg_gap.sort_values("Gap", ascending=False)
    if len(df_reg_gap):
        top_r = df_reg_gap.iloc[0]
        st.caption(
            f"**{top_r['Skill']}** — demand {int(top_r['Demand'])}, gap {float(top_r['Gap']):.2f}."
            + (" _(demo fallback — no England rows in Step C)_" if used_fallback else "")
        )
    else:
        st.info(f"No Step C rows for **{gap_pick}**. Check **UK Region** spelling in `step_c_gap_scores.csv`.")
    if len(df_reg_gap):
        fig_b = px.bar(
            df_reg_gap.sort_values("Gap"),
            x="Gap",
            y="Skill",
            orientation="h",
            color="Gap",
            color_continuous_scale=[[0, S2], [1, TEAL]],
            title=f"{gap_pick} — demand vs gap (gap score)",
        )
        fig_b.update_layout(coloraxis_showscale=False, yaxis_categoryorder="total ascending")
        fig_b.update_traces(texttemplate="%{x:.2f}", textposition="outside")
        show(fig_b, 420)

    _comm_ser = (
        df_c.loc[
            (df_c["UK Region"].astype(str).str.strip() == gap_pick)
            & (df_c["Skills"].astype(str).str.lower() == "communication"),
            "Gap_Score",
        ]
        if len(df_c) and "Skills" in df_c.columns and "UK Region" in df_c.columns
        else pd.Series(dtype=float)
    )
    comm_gap = float(_comm_ser.max()) if len(_comm_ser) else None
    _reg_tag = {"England": "ENG", "Scotland": "SCO", "Wales": "WAL", "Northern Ireland": "NI"}.get(
        gap_pick, gap_pick[:3].upper()
    )
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        f"Communication gap ({_reg_tag})",
        f"{comm_gap:.2f}" if comm_gap is not None else "—",
        f"Step C · {gap_pick}",
    )
    k2.metric("Recommendations", str(n_rec), "Step D rows")
    k3.metric("Top workshop skill", str(ws_df.iloc[0]["Skill"]) if len(ws_df) else "—", "1st row Step D")
    k4.metric("Clusters (Step C)", str(n_cl), "Distinct cluster names")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — GLOBAL COMPARISON
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "🌍 Global Comparison":
    gdf = gaming_global_frame(df_global) if df_global is not None else pd.DataFrame()
    use_live_global = not gdf.empty and "Country" in gdf.columns

    ahead_static = [
        ("Talent Acquisition", 18.73),
        ("Storytelling", 8.41),
        ("Team Management", 8.22),
        ("Unreal", 7.41),
        ("Maya", 6.57),
        ("C++", 6.35),
        ("Real-Time VFX", 4.61),
    ]
    behind_static = [
        ("CI/CD", 8.25),
        ("Python", 6.86),
        ("SQL", 5.68),
        ("Docker", 5.10),
        ("Kubernetes", 4.43),
        ("Linux", 4.41),
        ("AWS", 4.41),
    ]

    if use_live_global:
        by_c = top_countries_jobs(gdf).sort_values(ascending=False)
        n_ct = int(len(by_c))
        uk_jobs, uk_rank = 0, None
        for i, (country, cnt) in enumerate(by_c.items()):
            cl = str(country).strip().lower()
            if cl in {"united kingdom", "uk", "u.k.", "gb", "great britain"}:
                uk_jobs = int(cnt)
                uk_rank = i + 1
                break
        top10 = by_c.head(10)
        df_ct = pd.DataFrame({"Country": top10.index.astype(str), "Jobs": top10.values.astype(int)})
        df_ct["is_uk"] = df_ct["Country"].map(
            lambda x: str(x).strip().lower()
            in {"united kingdom", "uk", "u.k.", "gb", "great britain"}
        )
        ahead, behind = skill_share_diffs(gdf, top_n=7)
        st.markdown(f"### Global Comparison · `{n_ct} countries`")
        st.caption(
            f"Loaded from **`{global_source_name}`** — gaming-company rows; "
            f"skill mix = % of rows mentioning each skill token (comma-separated skills)."
        )
    else:
        by_c = None
        ahead, behind = [], []
        st.markdown("### Global Comparison · `81 Countries`")
        st.caption(
            "Reference dataset — place **`Combined_Data_cleaned.xlsx`** or **`Updated_27_02_26_-_Kabilan.xlsx`** "
            "in the project (sheet *Combined Data*) for live country counts and skill-mix bars."
        )
        ctries = [
            ("United States", 5604, False),
            ("India", 2374, False),
            ("Canada", 1914, False),
            ("United Kingdom", 1634, True),
            ("China", 998, False),
            ("Poland", 867, False),
            ("Germany", 575, False),
            ("Japan", 535, False),
            ("Australia", 447, False),
            ("France", 442, False),
        ]
        df_ct = pd.DataFrame(ctries, columns=["Country", "Jobs", "is_uk"])
        n_ct = 81
        uk_rank, uk_jobs = 4, 1634

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    if use_live_global and by_c is not None and len(by_c) > 0:
        c1.metric("UK rank (rows)", f"#{uk_rank}" if uk_rank else "—", f"{n_ct} countries")
        c2.metric("UK gaming rows", f"{uk_jobs:,}", "In workbook")
        c3.metric("Countries", f"{n_ct}", "≥1 gaming row")
        top_nm = str(by_c.index[0])
        c4.metric("Top country", top_nm[:22] + "…" if len(top_nm) > 22 else top_nm, f"{int(by_c.iloc[0]):,} rows")
    elif use_live_global and by_c is not None:
        c1.metric("UK rank (rows)", "—", "No country column data")
        c2.metric("UK gaming rows", f"{uk_jobs:,}", "In workbook")
        c3.metric("Countries", "0", "No rows after filter")
        c4.metric("Top country", "—", "Empty extract")
    else:
        c1.metric("UK Global Rank", "#4", "By gaming listings")
        c2.metric("Communication", "80/81", "Countries demand it")
        c3.metric("UK Comm. Share", "52.1%", "Ranks #1 globally")
        c4.metric("Most Similar", "France", "0.96 cosine sim.")

    st.markdown("---")
    st.subheader("Top countries by gaming job listings")
    st.caption("UK highlighted when present in top 10")
    df_ct["Type"] = df_ct["is_uk"].map({True: "United Kingdom", False: "Other"})
    fig_ct = px.bar(
        df_ct.sort_values("Jobs"),
        x="Jobs",
        y="Country",
        orientation="h",
        title="Top 10 countries — gaming job rows",
        color="Type",
        color_discrete_map={"United Kingdom": TEAL, "Other": DIM},
    )
    fig_ct.update_traces(texttemplate="%{x:,}", textposition="outside")
    fig_ct.update_layout(legend_title="")
    show(fig_ct, 420)
    if use_live_global and uk_rank:
        st.caption(f"UK at rank **{uk_rank}** with **{uk_jobs:,}** rows in this extract.")
    else:
        st.caption("UK highlighted · reference chart when no workbook is loaded")

    st.subheader("UK ahead / behind the world")
    col_a, col_b = st.columns(2)
    ahead_plot = ahead if ahead else ahead_static
    behind_plot = behind if behind else behind_static
    with col_a:
        cap_a = (
            "UK ahead — skill mention rate in UK job rows minus global rate (workbook)."
            if ahead
            else "UK ahead of the world — UK share % above global average (reference)"
        )
        st.caption(cap_a)
        fa = px.bar(
            pd.DataFrame(ahead_plot, columns=["Skill", "Diff"]).sort_values("Diff"),
            x="Diff",
            y="Skill",
            orientation="h",
            color_discrete_sequence=[GREEN],
            title="UK ahead",
        )
        fa.update_traces(texttemplate="+%{x:.2f}%", textposition="outside")
        fa.update_layout(showlegend=False)
        show(fa, 360)
    with col_b:
        cap_b = (
            "UK behind — lower mention rate vs all gaming rows (workbook)."
            if behind
            else "UK behind the world — future curriculum opportunities (reference)"
        )
        st.caption(cap_b)
        fb = px.bar(
            pd.DataFrame(behind_plot, columns=["Skill", "Abs"]).sort_values("Abs", ascending=False),
            x="Abs",
            y="Skill",
            orientation="h",
            color_discrete_sequence=[RED],
            title="UK behind",
        )
        fb.update_traces(texttemplate="-%{x:.2f}%", textposition="outside")
        fb.update_layout(showlegend=False)
        show(fb, 360)

    st.subheader("UK skill rankings vs global")
    st.caption("Full comparison")
    rnk = pd.DataFrame(
        [
            ["Communication", 52.12, 1, 55.06, 1, "↑ Ahead"],
            ["Talent Acquisition", 37.11, 2, 18.38, 4, "↑ Ahead"],
            ["Team Management", 33.67, 3, 25.45, 2, "↓ Behind"],
            ["Storytelling", 13.07, 6, 4.66, 37, "↑ Ahead"],
            ["Python", 12.99, 7, 19.85, 3, "↓ Behind"],
            ["C++", 12.71, 8, 6.36, 25, "↑ Ahead"],
            ["Unreal", 12.56, 9, 5.15, 31, "↑ Ahead"],
            ["CI/CD", 5.60, 18, 13.85, 6, "↓ Behind"],
        ],
        columns=["Skill", "UK Share %", "UK Rank", "Global Avg %", "Global Rank", "Trend"],
    )
    st.dataframe(rnk, use_container_width=True, hide_index=True)

    st.subheader("Countries most similar to UK")
    st.caption("Cosine similarity")
    sim = [
        ("France", 0.96),
        ("Japan", 0.95),
        ("USA", 0.94),
        ("Sweden", 0.93),
        ("Brazil", 0.93),
        ("Spain", 0.93),
        ("Malta", 0.92),
        ("Netherlands", 0.92),
    ]
    df_sim = pd.DataFrame(sim, columns=["Country", "Similarity"]).sort_values("Similarity")
    fig_sim = px.bar(
        df_sim,
        x="Similarity",
        y="Country",
        orientation="h",
        title="Countries with most similar skill profile to UK",
        color="Similarity",
        color_continuous_scale=[[0, DIM], [1, PURPLE]],
    )
    fig_sim.update_layout(coloraxis_showscale=False, xaxis_range=[0.88, 1.0])
    show(fig_sim, 360)
    st.caption("Cosine similarity — 1.0 = identical skill profile")

    if ahead:
        lead = ", ".join(f"{s} +{p:.1f}%" for s, p in ahead[:3])
        st.success(f"🏆 **From your workbook** — UK leads on: {lead}. Compare countries using the bar chart above.")
    else:
        st.success(
            "🏆 **Global conclusion** — UK world-class in creative skills — Storytelling +8.41%, "
            "Unreal +7.41%, C++ +6.35%. France, Japan and USA have the most similar profiles — "
            "UK skills open doors globally."
        )

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5 — CV EVALUATOR
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "📄 CV Evaluator":
    st.markdown("### CV Evaluator · `AI Powered`")
    st.caption(
        "Paste your CV · auto-extract skills · match UK gaming jobs · get personalised feedback"
    )
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**📤 Upload CV**\n\nPaste your CV text")
    with c2:
        st.markdown("**🔍 Extract Skills**\n\nAuto-detects skills")
    with c3:
        st.markdown(f"**📊 Match Jobs**\n\nvs {_job_listing_count(df_a):,} listing groups")
    with c4:
        st.markdown("**💡 Get Feedback**\n\nPersonalised advice")

    st.markdown("---")
    method = st.radio(
        "Input method",
        ["Paste CV text", "Upload PDF/TXT"],
        horizontal=True,
        label_visibility="collapsed",
        key="cv_input_method",
    )

    cv_text = ""
    if method == "Paste CV text":
        st.caption("Paste your CV here")
        st.caption("Include skills, experience, tools and education for best results")
        cv_text = st.text_area(
            "CV text",
            height=220,
            label_visibility="collapsed",
            key="cv_text_area",
            placeholder=(
                "Example: I have 3 years Unity and C++ experience, worked in agile teams using "
                "Jira and GitHub, strong communication and problem-solving skills, proficient in "
                "Python and SQL, experience with Maya and Photoshop..."
            ),
        )
    else:
        st.caption("Upload your CV (PDF or TXT)")
        up = st.file_uploader(
            "Upload CV",
            type=["pdf", "txt"],
            label_visibility="collapsed",
            key="cv_file_uploader",
        )
        if up is not None:
            try:
                if getattr(up, "type", "") == "text/plain" or str(up.name).lower().endswith(".txt"):
                    cv_text = up.read().decode("utf-8", errors="ignore")
                else:
                    data = up.read()
                    extracted = ""
                    try:
                        import pdfplumber

                        with pdfplumber.open(io.BytesIO(data)) as pdf:
                            extracted = "\n".join((p.extract_text() or "") for p in pdf.pages)
                    except Exception:
                        try:
                            import PyPDF2

                            reader = PyPDF2.PdfReader(io.BytesIO(data))
                            extracted = "\n".join((pg.extract_text() or "") for pg in reader.pages)
                        except Exception:
                            extracted = ""
                    if extracted and extracted.strip():
                        cv_text = extracted
                    elif up is not None:
                        # OCR fallback for scanned/image PDFs (optional dependencies).
                        # This keeps the app usable even if OCR isn't available.
                        ocr_text = ""
                        can_run_tesseract = bool(shutil.which("tesseract"))
                        try:
                            import fitz  # PyMuPDF
                            import pytesseract

                            if can_run_tesseract:
                                with st.spinner("Running OCR on the PDF (may take ~10–30s)…"):
                                    doc = fitz.open(stream=data, filetype="pdf")
                                    parts: list[str] = []
                                    max_pages = min(len(doc), 10)
                                    for i in range(max_pages):
                                        page = doc.load_page(i)
                                        pix = page.get_pixmap(dpi=200)
                                        img_bytes = pix.tobytes("png")
                                        try:
                                            from PIL import Image

                                            img = Image.open(io.BytesIO(img_bytes))
                                            parts.append(pytesseract.image_to_string(img) or "")
                                        except Exception:
                                            parts.append("")
                                    doc.close()
                                    ocr_text = "\n".join(parts).strip()
                        except Exception:
                            ocr_text = ""

                        if ocr_text:
                            cv_text = ocr_text
                            st.success("OCR completed — extracted text from the PDF.")
                        else:
                            if can_run_tesseract:
                                st.warning(
                                    "This PDF appears to contain little/no selectable text (often scanned image PDFs), "
                                    "and OCR did not produce usable text. Please paste your CV text instead."
                                )
                            else:
                                st.warning(
                                    "This PDF appears to contain little/no selectable text (often scanned image PDFs). "
                                    "To support any PDF, install OCR (Tesseract) or paste CV text instead."
                                )
                                st.caption(
                                    "Install OCR on Windows: install **Tesseract OCR**, then `pip install pymupdf pytesseract pillow`."
                                )
            except Exception:
                st.warning("Could not read the uploaded file. Please paste your CV text instead.")

    GAMING_SKILLS = [
        "communication",
        "team-management",
        "talent-acquisition",
        "cross-functional",
        "problem-solving",
        "python",
        "excel",
        "quality-control",
        "cpp",
        "unity",
        "unreal",
        "storytelling",
        "agile-development",
        "budget-management",
        "maya",
        "c#",
        "ms-office",
        "real-time-vfx",
        "photoshop",
        "data-analytics",
        "machine-learning",
        "java",
        "sql",
        "aws",
        "azure",
        "docker",
        "kubernetes",
        "linux",
        "git",
        "github",
        "jira",
        "confluence",
        "blender",
        "houdini",
        "rendering",
        "javascript",
        "typescript",
        "react",
        "node",
        "mongodb",
        "ci-cd",
        "user-experience-ux",
        "product-management",
        "salesforce",
        "tableau",
        "figma",
        "html",
        "css",
        "microservices",
        "networking",
        "timeline-management",
    ]
    JOB_CATS = {
        "Engineering & Dev": [
            "cpp",
            "c#",
            "python",
            "java",
            "javascript",
            "typescript",
            "unity",
            "unreal",
            "git",
            "github",
            "agile-development",
            "ci-cd",
            "docker",
            "kubernetes",
        ],
        "Art & Tech Art": [
            "maya",
            "photoshop",
            "blender",
            "houdini",
            "real-time-vfx",
            "rendering",
        ],
        "Game Design": [
            "unity",
            "unreal",
            "storytelling",
            "problem-solving",
            "communication",
            "user-experience-ux",
        ],
        "UI/UX": ["figma", "photoshop", "javascript", "html", "css", "communication"],
        "Data & Analytics": [
            "python",
            "sql",
            "data-analytics",
            "machine-learning",
            "excel",
            "aws",
            "azure",
            "tableau",
        ],
        "Cloud & DevOps": [
            "aws",
            "azure",
            "docker",
            "kubernetes",
            "linux",
            "ci-cd",
            "python",
            "networking",
            "microservices",
        ],
        "HR & Recruiting": [
            "talent-acquisition",
            "communication",
            "team-management",
            "excel",
            "ms-office",
        ],
        "Marketing & Adv": [
            "communication",
            "storytelling",
            "data-analytics",
            "budget-management",
        ],
        "Production": [
            "agile-development",
            "jira",
            "confluence",
            "team-management",
            "communication",
            "budget-management",
        ],
        "Biz Dev & Sales": [
            "communication",
            "budget-management",
            "cross-functional",
            "salesforce",
        ],
    }
    TOP_P = [
        "communication",
        "team-management",
        "python",
        "cpp",
        "unity",
        "agile-development",
        "problem-solving",
        "excel",
        "talent-acquisition",
    ]

    if st.button("Analyse My CV", type="primary"):
        if not cv_text.strip():
            st.warning("Please paste your CV text first.")
        else:
            txt = cv_text.lower()
            found = []
            for sk in GAMING_SKILLS:
                variants = [sk, sk.replace("-", " "), cn(sk).lower()]
                if any(v in txt for v in variants) and sk not in found:
                    found.append(sk)
            miss = [
                s
                for s in TOP_P
                if s not in found and s.replace("-", " ") not in txt
            ]
            scores = []
            for cat, skills in JOB_CATS.items():
                m = [s for s in skills if s in found]
                score = round(len(m) / len(skills) * 100, 1)
                scores.append((cat, score, len(m), len(skills)))
            scores.sort(key=lambda x: x[1], reverse=True)
            overall = round(len(found) / len(GAMING_SKILLS) * 100, 1)

            st.markdown("---")
            st.subheader("Your analysis results")
            st.caption("CV match")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Skills Found", str(len(found)), f"of {len(GAMING_SKILLS)} tracked")
            c2.metric("Gaming Match", f"{overall}%", "Industry relevance")
            c3.metric("Best Job Fit", scores[0][0].split("&")[0].strip(), f"{scores[0][1]:.0f}% match")
            c4.metric("Priority Gaps", str(len(miss)), "Missing top skills")

            st.markdown("---")
            cl, cr = st.columns(2)
            with cl:
                st.caption(f"{len(found)} gaming skills detected in your CV")
                if found:
                    st.success(" · ".join(cn(s) for s in sorted(found)))
                else:
                    st.caption("No skills detected — add specific tool names")
                st.markdown("**Missing high-priority skills**")
                st.caption("Most demanded UK gaming skills not in your CV")
                if miss:
                    st.error(" · ".join(cn(s) for s in miss))
                else:
                    st.success("All high-priority skills present!")
            with cr:
                st.caption("Job category match scores — how well you fit each gaming role type")
                df_cm = pd.DataFrame(
                    [(c, s, m, t) for c, s, m, t in scores],
                    columns=["Category", "Score %", "Matched", "Total"],
                ).sort_values("Score %", ascending=True)
                fig_cm = px.bar(
                    df_cm,
                    x="Score %",
                    y="Category",
                    orientation="h",
                    title="Job category match scores",
                    color="Score %",
                    color_continuous_scale=[[0, RED], [0.4, AMBER], [1, GREEN]],
                )
                fig_cm.update_traces(texttemplate="%{x:.0f}%", textposition="outside")
                fig_cm.update_layout(coloraxis_showscale=False)
                show(fig_cm, 380)

            st.subheader("Top job recommendations")
            st.caption("Best-fit roles")
            t1, t2, t3 = st.columns(3)
            for i, (cat, score, matched, total) in enumerate(scores[:3]):
                col = (t1, t2, t3)[i]
                with col:
                    st.metric(cat, f"{score:.0f}%", f"{matched} of {total} skills")

            st.markdown("---")
            if overall == 0:
                advice = (
                    "No gaming skills detected. Add tools like Unity, Python, C++, Unreal to your "
                    "CV using exact industry terms."
                )
            elif overall >= 60:
                advice = (
                    f"Excellent gaming profile! You match best for {scores[0][0]}. Focus on boosting "
                    f"your {cn(miss[0]) if miss else 'portfolio'} to reach senior roles."
                )
            elif overall >= 30:
                advice = (
                    f"Good foundation. Strengthen by adding {', '.join(cn(s) for s in miss[:3])} "
                    f"— these appear in the most UK gaming job ads."
                )
            else:
                advice = (
                    f"Add more gaming-specific skills. Top recommendations: "
                    f"{', '.join(cn(s) for s in miss[:4])}. Consider SideFest workshops."
                )
            st.info(f"💡 **Career advice** — {advice}")

