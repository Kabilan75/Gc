"""
UK Gaming Industry — Skill Intelligence Dashboard
University of Leicester | AI for Business Intelligence | Kabilan 2025
"""
from __future__ import annotations
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

# ── Minimal safe CSS  (only colours, no layout overrides) ─────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #0C1422; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stRadio div { color: #CBD5E1 !important; }
.stApp { background-color: #05090F; color: #F0F4F8; }
.block-container { padding-top: 1.5rem; }
h1, h2, h3 { color: #F0F4F8 !important; }
p, li { color: #CBD5E1; }
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
TOP15_HTML = [
    ("Communication", 610),
    ("Team Management", 379),
    ("Talent Acquisition", 343),
    ("Cross-Functional", 180),
    ("Problem Solving", 139),
    ("Python", 139),
    ("Excel", 136),
    ("Quality Control", 135),
    ("C++", 134),
    ("Unity", 133),
    ("Unreal", 130),
    ("Storytelling", 129),
    ("Agile Dev", 127),
    ("Budget Mgmt", 118),
    ("Maya", 100),
]
CAT_PIE_HTML = {
    "Soft Skills": 2499,
    "Other": 1457,
    "Tools": 893,
    "Programming": 639,
    "3D Art": 575,
    "Game Engines": 512,
    "Cloud": 373,
}
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

# ── Plotly dark theme helper ──────────────────────────────────────────────────
def _dark(fig, h=None):
    if h:
        fig.update_layout(height=h)
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=S1, paper_bgcolor=S1,
        font=dict(color=MUTED, size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        title_font=dict(color="#F0F4F8", size=14),
        colorway=CHART_COLS,
        hoverlabel=dict(bgcolor=S2, font_color="#E2E8F0"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)",
                     linecolor="rgba(255,255,255,0.08)",
                     tickfont=dict(color=DIM))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)",
                     linecolor="rgba(255,255,255,0.08)",
                     tickfont=dict(color=DIM))
    return fig

def show(fig, h=None):
    st.plotly_chart(_dark(fig, h), use_container_width=True)

# ── Load data ─────────────────────────────────────────────────────────────────
def _probe_live() -> tuple[bool, bool, bool, bool]:
    a, la = load_a()
    b, lb = load_b()
    c, lc = load_c()
    d, ld = load_d()
    del a, b, c, d
    return la, lb, lc, ld


live_a, live_b, live_c, live_d = _probe_live()
all_live = live_a and live_b and live_c and live_d

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎮 Skill Intelligence")
    st.markdown("**UK Gaming Industry**")
    st.markdown("---")

    tab = st.radio(
        "Navigation",
        ["📊 UK Overview",
         "🗺️ Regional Analysis",
         "🤖 AI Gap Analysis",
         "🌍 Global Comparison",
         "📄 CV Evaluator"],
    )

    st.markdown("---")
    if all_live:
        st.success("📡 Live CSV data loaded")
    else:
        st.info("📋 Using demo data")

    st.markdown("---")
    st.markdown("""
**University of Leicester**  
AI for Business Intelligence  
Kabilan · 2025  
Data: Jul–Oct 2025
""")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — UK OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if tab == "📊 UK Overview":
    st.markdown("### UK Overview · `1,121 Jobs`")
    st.caption("National snapshot · 1,121 UK gaming job listings · Jul–Oct 2025")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Job Ads", "1,121", "UK gaming companies")
    c2.metric("Unique Skills", "352", "Across all listings")
    c3.metric("Skill Rows", "6,948", "After cleaning")
    c4.metric("UK Regions", "4", "ENG · SCO · WAL · NI")

    st.markdown("---")
    st.subheader("Top 15 skills by demand")
    st.caption("Total occurrences — total mentions across all 1,121 job listings")

    col_l, col_r = st.columns(2)

    with col_l:
        df_top = pd.DataFrame(TOP15_HTML, columns=["Skill", "Count"])
        fig = px.bar(
            df_top.sort_values("Count"),
            x="Count",
            y="Skill",
            orientation="h",
            title="Skill occurrences",
            color_discrete_sequence=[TEAL],
        )
        fig.update_layout(showlegend=False, yaxis_categoryorder="total ascending")
        fig.update_traces(texttemplate="%{x:,}", textposition="outside")
        show(fig, 460)

    with col_r:
        fig_pie = px.pie(
            values=list(CAT_PIE_HTML.values()),
            names=list(CAT_PIE_HTML.keys()),
            hole=0.58,
            title="Skill category distribution",
            color_discrete_sequence=[TEAL, DIM, BLUE, PURPLE, AMBER, GREEN, RED],
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=True, legend=dict(font=dict(size=11)))
        show(fig_pie, 320)
        st.caption("7 categories · 6,948 cleaned skill rows")

    st.subheader("Skill hierarchy — top 10")
    st.caption("Cross-sector reach")
    hier = pd.DataFrame(
        [
            ["Communication", 560, 1060, 1620, "All 3 tiers", "31%"],
            ["Team Management", 335, 696, 1031, "All 3 tiers", "21%"],
            ["Talent Acquisition", 317, 688, 1005, "All 3 tiers", "18%"],
            ["Cross-Functional", 168, 396, 564, "All 3 tiers", "10%"],
            ["Python", 134, 267, 401, "All 3 tiers", "7%"],
            ["Excel", 124, 302, 421, "All 3 tiers", "7%"],
            ["Quality Control", 124, "—", 314, "Gaming+Trans", "7%"],
            ["Problem Solving", 127, 233, 360, "All 3 tiers", "8%"],
            ["Unity", 122, "—", "—", "Gaming ONLY", "6%"],
            ["C++", 121, "—", "—", "Gaming ONLY", "6%"],
        ],
        columns=["Skill", "Gaming", "Tech", "Transferable", "Scope", "Coverage"],
    )
    st.dataframe(hier, use_container_width=True, hide_index=True)

    st.info(
        "🎯 **Top finding** — Communication leads ALL 3 tiers — 560 gaming, 1,060 tech, "
        "1,620 transferable. Unity and C++ are gaming-exclusive. "
        "Top 15 skills = 42.2% of all demand."
    )

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — REGIONAL ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "🗺️ Regional Analysis":
    st.markdown("### Regional Analysis · `4 Regions`")
    st.caption(
        "England · Scotland · Wales · Northern Ireland — normalised per 100k population"
    )
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("England /100k", "0.93", "Communication")
    c2.metric("Scotland /100k", "0.26", "C++ hub")
    c3.metric("Wales Unity", "0.00", "Zero game engines")
    c4.metric("NI Cloud", "0.00", "Zero cloud demand")

    st.markdown("---")
    st.subheader("Top 5 skills per region")
    st.caption("Count · per 100k")
    regional = {
        "England": [
            ("Communication", 527, 0.93),
            ("Team Management", 318, 0.56),
            ("Talent Acquisition", 294, 0.52),
            ("Cross-Functional", 158, 0.28),
            ("Python", 127, 0.22),
        ],
        "Scotland": [
            ("Communication", 23, 0.42),
            ("Talent Acquisition", 20, 0.37),
            ("Agile Dev", 18, 0.33),
            ("Team Management", 15, 0.27),
            ("C++", 14, 0.26),
        ],
        "Wales": [
            ("Azure", 4, 0.13),
            ("Back-End Dev", 3, 0.10),
            ("CI/CD", 3, 0.10),
            ("Communication", 3, 0.10),
            ("GitHub", 3, 0.10),
        ],
        "N. Ireland": [
            ("Communication", 7, 0.37),
            ("Java", 5, 0.26),
            ("Microservices", 5, 0.26),
            ("CI/CD", 4, 0.21),
            ("Data Analytics", 4, 0.21),
        ],
    }
    cols4 = st.columns(4)
    for i, (reg, skills) in enumerate(regional.items()):
        with cols4[i]:
            st.subheader(reg)
            rows = [{"Skill": s, "Count": c, "/100k": p} for s, c, p in skills]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.subheader("Skill demand heatmap")
    st.caption("Per 100k population · Top 10 skills × 4 regions")
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

    st.subheader("Cluster composition")
    st.caption("Per 100k population · K-Means grouping")
    fig_cl = go.Figure()
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
        title="6 AI clusters stacked per region",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    show(fig_cl, 400)
    st.caption("Game Dev · Soft Skills · Proj Mgmt · Creative · Biz Tools · Cloud")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI GAP ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "🤖 AI Gap Analysis":
    st.markdown("### AI Gap Analysis · `520 Gap Scores`")
    st.caption(
        "TF-IDF · K-Means clustering · Location Quotient gap scoring · Workshop recommender"
    )
    st.markdown("---")

    st.subheader("The AI pipeline")
    st.caption("Step A → B → C → D")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown("**A · Data Prep**\n\n6,948 rows · 352 skills")
    with p2:
        st.markdown("**B · K-Means AI**\n\nTF-IDF · 6 clusters")
    with p3:
        st.markdown("**C · Gap Scoring**\n\nLoc. Quotient · 520")
    with p4:
        st.markdown("**D · Recommender**\n\nTop 5/region · 20 total")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    gv = {
        "England": [5.07, 5.09, 5.09, 5.21, 5.26, 5.09],
        "Scotland": [4.74, 4.25, 4.62, 4.82, 4.75, 4.82],
        "Wales": [3.41, 3.50, 3.59, 4.18, 4.64, 4.66],
        "N.Ireland": [2.77, 0.00, 3.90, 4.63, 4.52, 4.69],
    }
    gcl = ["Biz Tools", "Cloud", "Game Dev", "Proj Mgmt", "Soft Skills", "Creative"]
    z_g = [[gv[r][i] for i in range(6)] for r in gv]

    with col_l:
        st.caption("Average gap score — region × cluster")
        st.caption("Location Quotient · darker = more urgent · 0.00 = zero demand")
        fig_ghm = go.Figure(
            go.Heatmap(
                z=z_g,
                x=gcl,
                y=list(gv.keys()),
                text=[[f"{v:.2f}" for v in row] for row in z_g],
                texttemplate="%{text}",
                colorscale=[[0, S2], [0.35, "#0D2540"], [1, TEAL]],
                hovertemplate="<b>%{y} — %{x}</b><br>Gap: %{z:.2f}<extra></extra>",
            )
        )
        fig_ghm.update_layout(title="Region × cluster gap scores", yaxis=dict(autorange="reversed"))
        show(fig_ghm, 340)
        st.warning(
            "⚠️ **N. Ireland Cloud = 0.00** — Zero employer demand. "
            "England 5.07–5.26 across ALL clusters — urgent everywhere."
        )

    with col_r:
        st.caption("Workshop recommendations")
        st.caption("Step D output — ranked by gap score · priority coded")
        ws_df = pd.DataFrame(
            WORKSHOP_HTML,
            columns=["Region", "Skill", "Demand", "Gap", "Priority"],
        )
        st.dataframe(ws_df, use_container_width=True, hide_index=True)

    st.subheader("Demand vs gap score — England")
    st.caption("Scatter insight · each row = one skill · gap score out of 10")
    st.caption(
        "Communication sits alone — 527 demand, gap 10.0. Nothing else comes close."
    )
    df_eng = pd.DataFrame(
        [(a, b, c) for a, b, c, _ in GAP_ENG_BARS], columns=["Skill", "Demand", "Gap"]
    )
    fig_b = px.bar(
        df_eng.sort_values("Gap"),
        x="Gap",
        y="Skill",
        orientation="h",
        color="Gap",
        color_continuous_scale=[[0, S2], [1, TEAL]],
        title="England — demand vs gap (gap score)",
    )
    fig_b.update_layout(coloraxis_showscale=False, yaxis_categoryorder="total ascending")
    fig_b.update_traces(texttemplate="%{x:.2f}", textposition="outside")
    show(fig_b, 420)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Communication Gap", "10.0", "England — maximum")
    k2.metric("Recommendations", "20", "5 per UK region")
    k3.metric("#1 All 4 Regions", "Comm.", "Communication everywhere")
    k4.metric("Clusters Found", "6", "K-Means K=6")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — GLOBAL COMPARISON
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "🌍 Global Comparison":
    st.markdown("### Global Comparison · `81 Countries`")
    st.caption(
        "UK vs 81 countries — fair skill share % · not raw counts · 27,898 global jobs"
    )
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("UK Global Rank", "#4", "By gaming listings")
    c2.metric("Communication", "80/81", "Countries demand it")
    c3.metric("UK Comm. Share", "52.1%", "Ranks #1 globally")
    c4.metric("Most Similar", "France", "0.96 cosine sim.")

    st.markdown("---")
    st.subheader("Top countries by gaming job listings")
    st.caption("UK highlighted")
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
    df_ct["Type"] = df_ct["is_uk"].map({True: "United Kingdom", False: "Other"})
    fig_ct = px.bar(
        df_ct.sort_values("Jobs"),
        x="Jobs",
        y="Country",
        orientation="h",
        title="Top 10 countries — unique gaming job listings",
        color="Type",
        color_discrete_map={"United Kingdom": TEAL, "Other": DIM},
    )
    fig_ct.update_traces(texttemplate="%{x:,}", textposition="outside")
    fig_ct.update_layout(legend_title="")
    show(fig_ct, 420)
    st.caption("UK highlighted · 4th globally with 1,634 jobs")

    st.subheader("UK ahead / behind the world")
    col_a, col_b = st.columns(2)
    ahead = [
        ("Talent Acquisition", 18.73),
        ("Storytelling", 8.41),
        ("Team Management", 8.22),
        ("Unreal", 7.41),
        ("Maya", 6.57),
        ("C++", 6.35),
        ("Real-Time VFX", 4.61),
    ]
    behind = [
        ("CI/CD", 8.25),
        ("Python", 6.86),
        ("SQL", 5.68),
        ("Docker", 5.10),
        ("Kubernetes", 4.43),
        ("Linux", 4.41),
        ("AWS", 4.41),
    ]
    with col_a:
        st.caption("UK ahead of the world — UK share % above global average")
        fa = px.bar(
            pd.DataFrame(ahead, columns=["Skill", "Diff"]).sort_values("Diff"),
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
        st.caption("UK behind the world — future curriculum opportunities for SideFest")
        fb = px.bar(
            pd.DataFrame(behind, columns=["Skill", "Abs"]).sort_values("Abs", ascending=False),
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
        st.markdown("**📊 Match Jobs**\n\nvs 1,121 UK gaming jobs")
    with c4:
        st.markdown("**💡 Get Feedback**\n\nPersonalised advice")

    st.markdown("---")
    st.caption("Paste your CV here")
    st.caption("Include skills, experience, tools and education for best results")
    cv_text = st.text_area(
        "CV text",
        height=220,
        label_visibility="collapsed",
        placeholder=(
            "Example: I have 3 years Unity and C++ experience, worked in agile teams using "
            "Jira and GitHub, strong communication and problem-solving skills, proficient in "
            "Python and SQL, experience with Maya and Photoshop..."
        ),
    )

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
        "c++",
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
            "c++",
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
        "c++",
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

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "UK Gaming Industry — Skill Intelligence · University of Leicester · "
    "AI for Business Intelligence · Kabilan · 2025"
)
