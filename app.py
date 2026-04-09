"""
UK Gaming Industry — Skill Intelligence Dashboard
University of Leicester | AI for Business Intelligence | Kabilan 2025
"""
from __future__ import annotations
import io, warnings
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
NAVY   = "#05090F"
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
REGION_COLS = {
    "England": BLUE, "Scotland": GREEN,
    "Wales": AMBER, "Northern Ireland": PURPLE,
}
CLUSTER_COLS = {
    "Game Development & Programming":    BLUE,
    "Soft Skills & Business Development": PURPLE,
    "Project & Development Management":  GREEN,
    "Soft Skills & Creative Production":  "#F472B6",
    "Business Tools & Productivity":     AMBER,
    "Cloud, Infrastructure & DevOps":    TEAL,
}
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
def load_excel():
    for name in ("Combined_Data_cleaned.xlsx",
                 "Updated_27_02_26_-_Kabilan.xlsx",
                 "Updated 27.02.26 - Kabilan (1).xlsx"):
        p = _find(name)
        if p:
            try:
                return pd.read_excel(p, sheet_name="Combined Data"), True
            except Exception:
                continue
    return None, False

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
df_a, live_a = load_a()
df_b, live_b = load_b()
df_c, live_c = load_c()
df_d, live_d = load_d()

df_a["Skill_Display"] = df_a["Skills"].apply(cn)
df_b["Skill_Display"] = df_b["Skills"].apply(cn)
if "Skills" in df_c.columns:
    df_c["Skill_Display"] = df_c["Skills"].apply(cn)
if "Skills" in df_d.columns:
    df_d["Skill_Display"] = df_d["Skills"].apply(cn)

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
    st.title("📊 UK Gaming — Skill Overview")
    st.caption("National snapshot · 1,121 UK gaming job listings · Jul–Oct 2025")
    st.markdown("---")

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Job Ads",  "1,121",  "UK gaming companies")
    c2.metric("Unique Skills",  "352",    "Across all listings")
    c3.metric("Skill Rows",     "6,948",  "After cleaning")
    c4.metric("UK Regions",     "4",      "ENG · SCO · WAL · NI")

    st.markdown("---")

    # View toggle
    st.subheader("Job Demand Analysis")
    view = st.radio(
        "View by:",
        ["Total Occurrences", "Unique Job Ads", "Coverage %"],
        horizontal=True,
    )

    unique_ads = {
        "Communication": 560, "Team Management": 335,
        "Talent Acquisition": 317, "Cross-Functional": 168,
        "Problem Solving": 139, "Python": 139, "Excel": 136,
        "Quality Control": 135, "C++": 134, "Unity": 133,
        "Unreal": 130, "Storytelling": 129,
        "Agile Development": 127, "Budget Management": 118, "Maya": 100,
    }

    col_l, col_r = st.columns(2)

    with col_l:
        if view == "Total Occurrences":
            df_v = (df_a["Skill_Display"]
                    .value_counts().head(15)
                    .reset_index())
            df_v.columns = ["Skill", "Count"]
            fig = px.bar(
                df_v, x="Count", y="Skill", orientation="h",
                title="Top 15 Skills — Total Occurrences",
                color="Count",
                color_continuous_scale=[[0, S2], [1, TEAL]])
            fig.update_layout(coloraxis_showscale=False,
                              yaxis_categoryorder="total ascending")
            fig.update_traces(texttemplate="%{x:,}",
                              textposition="outside")
            show(fig, 460)
        elif view == "Unique Job Ads":
            df_u = pd.DataFrame(
                unique_ads.items(),
                columns=["Skill", "UniqueAds"]).sort_values("UniqueAds")
            fig = px.bar(
                df_u, x="UniqueAds", y="Skill", orientation="h",
                title="Top 15 Skills — Unique Job Ads",
                color="UniqueAds",
                color_continuous_scale=[[0, S2], [1, PURPLE]])
            fig.update_layout(coloraxis_showscale=False)
            fig.update_traces(texttemplate="%{x}",
                              textposition="outside")
            show(fig, 460)
        else:
            df_cov = pd.DataFrame(
                [(k, round(v / 1121 * 100, 1))
                 for k, v in unique_ads.items()],
                columns=["Skill", "Coverage %"]).sort_values("Coverage %")
            fig = px.bar(
                df_cov, x="Coverage %", y="Skill", orientation="h",
                title="Skill Coverage — % of All 1,121 Gaming Jobs",
                color="Coverage %",
                color_continuous_scale=[[0, S2], [1, AMBER]])
            fig.update_layout(coloraxis_showscale=False)
            fig.update_traces(texttemplate="%{x:.1f}%",
                              textposition="outside")
            show(fig, 460)

    with col_r:
        cats = {
            "Soft Skills": 2499, "Other": 1457, "Tools & Software": 893,
            "Programming": 639, "3D Art & Design": 575,
            "Game Engines": 512, "Cloud & DevOps": 373,
        }
        fig_pie = px.pie(
            values=list(cats.values()),
            names=list(cats.keys()),
            hole=0.54,
            title="Skill Category Mix",
            color_discrete_sequence=[TEAL, DIM, BLUE, PURPLE,
                                     AMBER, GREEN, RED])
        fig_pie.update_traces(textposition="inside",
                              textinfo="percent+label")
        fig_pie.update_layout(showlegend=False)
        show(fig_pie, 280)

        job_cats = {
            "Art & Tech Art": 172, "Engineering & Dev": 167,
            "Marketing": 73, "Biz Dev & Sales": 57,
            "Accounting": 52, "Game Design": 52,
            "Product & PM": 50, "HR & Recruiting": 45,
            "Animation": 43, "UI/UX": 39,
        }
        df_jc = pd.DataFrame(
            job_cats.items(),
            columns=["Category", "Jobs"]).sort_values("Jobs")
        fig_jc = px.bar(
            df_jc, x="Jobs", y="Category", orientation="h",
            title="Top 10 Job Categories (31 total)",
            color="Jobs",
            color_continuous_scale=[[0, S2], [1, GREEN]])
        fig_jc.update_layout(coloraxis_showscale=False)
        show(fig_jc, 280)

    # Hierarchy table
    st.subheader("Skill Hierarchy — Top 10")
    st.caption("Cross-sector reach across Gaming, Tech and Transferable roles")
    hier = pd.DataFrame([
        ["Communication",      560, 1060, 1620, "All 3 tiers",  "31.0%"],
        ["Team Management",    335,  696, 1031, "All 3 tiers",  "21.1%"],
        ["Talent Acquisition", 317,  688, 1005, "All 3 tiers",  "18.2%"],
        ["Cross-Functional",   168,  396,  564, "All 3 tiers",   "9.8%"],
        ["Python",             134,  267,  401, "All 3 tiers",   "7.3%"],
        ["Excel",              124,  302,  421, "All 3 tiers",   "7.2%"],
        ["Quality Control",    124,  "—",  314, "Gaming+Trans",  "6.5%"],
        ["Problem Solving",    127,  233,  360, "All 3 tiers",   "7.9%"],
        ["Unity",              122,  "—",  "—", "Gaming ONLY",   "6.1%"],
        ["C++",                121,  "—",  "—", "Gaming ONLY",   "6.4%"],
    ], columns=["Skill", "Gaming", "Tech",
                "Transferable", "Scope", "Coverage"])
    st.dataframe(hier, use_container_width=True, hide_index=True)

    st.info("🎯 **Top Finding** — Communication leads ALL 3 tiers: "
            "560 gaming, 1,060 tech, 1,620 transferable posts. "
            "Unity and C++ are gaming-exclusive. "
            "Top 15 skills = 42.2% of all demand.")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — REGIONAL ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "🗺️ Regional Analysis":
    st.title("🗺️ Regional Analysis")
    st.caption("England · Scotland · Wales · Northern Ireland — per 100k population")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("England /100k",  "0.93", "Communication — peak")
    c2.metric("Scotland /100k", "0.26", "C++ hub")
    c3.metric("Wales Unity",    "0.00", "Zero game engine demand")
    c4.metric("NI Cloud",       "0.00", "Zero cloud demand")

    st.markdown("---")

    # Live heatmap
    st.subheader("Skill Demand Heatmap — Per 100k Population")
    regions = list(POP.keys())
    top_skills = (df_b["Skill_Display"]
                  .value_counts().head(15).index.tolist())
    hm_z, hm_t = [], []
    for sk in top_skills:
        rv, rt = [], []
        for rg in regions:
            cnt = len(df_b[(df_b["Skill_Display"] == sk) &
                           (df_b["UK Region"] == rg)])
            val = round(cnt / POP[rg] * 100_000, 2)
            rv.append(val)
            rt.append(f"{val:.2f}")
        hm_z.append(rv)
        hm_t.append(rt)
    fig_hm = go.Figure(go.Heatmap(
        z=hm_z, x=regions, y=top_skills,
        text=hm_t, texttemplate="%{text}",
        colorscale=[[0, S2], [0.3, "#0D3A6E"],
                    [0.65, "#0D7A8E"], [1, TEAL]],
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.2f} /100k<extra></extra>",
    ))
    fig_hm.update_layout(title="Gaming Skill Demand per 100k Population")
    show(fig_hm, 500)

    # Regional top 5 cards
    st.subheader("Top 5 Skills per Region")
    regional = {
        "England": [("Communication",527,0.93),("Team Management",318,0.56),
                    ("Talent Acquisition",294,0.52),
                    ("Cross-Functional",158,0.28),("Python",127,0.22)],
        "Scotland":[("Communication",23,0.42),("Talent Acquisition",20,0.37),
                    ("Agile Development",18,0.33),
                    ("Team Management",15,0.27),("C++",14,0.26)],
        "Wales":   [("Azure",4,0.13),("Back-End Dev",3,0.10),
                    ("CI/CD",3,0.10),("Communication",3,0.10),
                    ("GitHub",3,0.10)],
        "N.Ireland":[("Communication",7,0.37),("Java",5,0.26),
                     ("Microservices",5,0.26),("CI/CD",4,0.21),
                     ("Data Analytics",4,0.21)],
    }
    cols4 = st.columns(4)
    for i, (reg, skills) in enumerate(regional.items()):
        with cols4[i]:
            st.subheader(reg)
            rows = [{"Skill": s, "Count": c, "/100k": p}
                    for s, c, p in skills]
            st.dataframe(pd.DataFrame(rows),
                         use_container_width=True,
                         hide_index=True)

    # Cluster stacked bar
    st.subheader("Skill Cluster Composition — Per 100k")
    cl_d = {
        "Game Dev & Programming":    [3.55, 2.19, 1.06, 1.88],
        "Soft Skills & Biz Dev":     [3.55, 1.60, 0.47, 1.20],
        "Project & Dev Mgmt":        [1.49, 0.93, 0.09, 0.58],
        "Soft Skills & Creative":    [1.45, 0.44, 0.16, 0.21],
        "Business Tools":            [0.72, 0.47, 0.22, 0.37],
        "Cloud & DevOps":            [0.71, 0.18, 0.28, 0.00],
    }
    fig_cl = go.Figure()
    colors_cl = [BLUE, PURPLE, GREEN, "#F472B6", AMBER, TEAL]
    for i, (cl, vals) in enumerate(cl_d.items()):
        fig_cl.add_trace(go.Bar(
            name=cl, x=regions, y=vals,
            marker_color=colors_cl[i],
            marker_line_width=0))
    fig_cl.update_layout(
        barmode="stack",
        title="Cluster Composition per Region (per 100k)",
        legend=dict(orientation="h", y=1.08, x=0))
    show(fig_cl, 420)

    # Region drilldown
    st.subheader("Region Drilldown")
    sel = st.selectbox("Select region:", list(POP.keys()))
    drill = (df_b[df_b["UK Region"] == sel]["Skill_Display"]
             .value_counts().head(12).reset_index())
    drill.columns = ["Skill", "Count"]
    fig_dr = px.bar(
        drill, x="Count", y="Skill", orientation="h",
        title=f"Top 12 Skills — {sel}",
        color="Count",
        color_continuous_scale=[[0, S2],
                                 [1, REGION_COLS.get(sel, TEAL)]])
    fig_dr.update_layout(coloraxis_showscale=False,
                         yaxis_categoryorder="total ascending")
    fig_dr.update_traces(texttemplate="%{x}", textposition="outside")
    show(fig_dr, 420)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI GAP ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "🤖 AI Gap Analysis":
    st.title("🤖 AI Gap Analysis")
    st.caption("TF-IDF · K-Means · Location Quotient gap scoring · Workshop recommender")
    st.markdown("---")

    # Pipeline
    st.subheader("The AI Pipeline — Step A → B → C → D")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.info("**Step A — Data Prep**\n\n6,948 rows · 352 skills")
    with p2:
        st.info("**Step B — K-Means AI**\n\nTF-IDF encoding · 6 clusters")
    with p3:
        st.warning("**Step C — Gap Scoring**\n\nLocation Quotient · 520 scores")
    with p4:
        st.success("**Step D — Recommender**\n\nTop 5/region · 20 total")

    st.markdown("---")

    # Gap heatmap + insights
    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.subheader("Gap Score Heatmap — Region × Cluster")
        gv = {
            "England":         [5.07, 5.09, 5.09, 5.21, 5.26, 5.09],
            "Scotland":        [4.74, 4.25, 4.62, 4.82, 4.75, 4.82],
            "Wales":           [3.41, 3.50, 3.59, 4.18, 4.64, 4.66],
            "Northern Ireland":[2.77, 0.00, 3.90, 4.63, 4.52, 4.69],
        }
        gcl = ["Biz Tools","Cloud","Game Dev",
               "Proj Mgmt","Soft Skills","Creative"]
        z_g = [[gv[r][i] for i in range(6)] for r in gv]
        fig_ghm = go.Figure(go.Heatmap(
            z=z_g, x=gcl, y=list(gv.keys()),
            colorscale=[[0, S2], [0.3, "#0D2540"],
                        [0.7, "#0D7A8E"], [1, TEAL]],
            text=[[f"{v:.2f}" for v in row] for row in z_g],
            texttemplate="%{text}",
            hovertemplate="<b>%{y} — %{x}</b><br>Gap: %{z:.2f}<extra></extra>",
        ))
        fig_ghm.update_layout(title="Average Gap Score (0–10 scale)")
        show(fig_ghm, 280)

        df_ghm = pd.DataFrame(
            z_g, index=list(gv.keys()), columns=gcl).round(2)
        df_ghm.index.name = "Region"
        st.dataframe(df_ghm.reset_index(),
                     use_container_width=True, hide_index=True)

    with col_r:
        st.subheader("Key Insights")
        st.error("🔴 **England** — Gap scores 5.07–5.26 across ALL 6 clusters. Urgent everywhere.")
        st.warning("⚠️ **N. Ireland** — Cloud/DevOps = 0.00. Zero employer demand. No cloud workshops there.")
        st.info("💡 **Soft Skills cluster** = highest avg gap in England at 5.26, driven by Communication at 10.0.")

    # Scatter
    st.subheader("Demand vs Gap Score — England")
    st.caption("Each dot = one skill · top right = most urgent to teach")
    eng_c = (df_c[df_c["UK Region"] == "England"].copy()
             if "UK Region" in df_c.columns else df_c.copy())
    if {"Demand", "Gap_Score", "Skill_Display"}.issubset(eng_c.columns):
        fig_sc = px.scatter(
            eng_c, x="Demand", y="Gap_Score",
            color="Cluster_Name" if "Cluster_Name" in eng_c.columns else None,
            hover_name="Skill_Display",
            size="Demand", size_max=30,
            title="Demand vs Gap Score — England",
            color_discrete_sequence=CHART_COLS)
        try:
            fig_sc.add_annotation(
                x=527, y=10.0, text="◀ Communication",
                showarrow=False,
                font=dict(color=TEAL, size=11))
        except Exception:
            pass
        show(fig_sc, 420)

    # Box plot
    st.subheader("Gap Score Distribution by Region")
    if {"UK Region", "Gap_Score"}.issubset(df_c.columns):
        fig_box = px.box(
            df_c, x="UK Region", y="Gap_Score",
            color="UK Region",
            title="Gap Score Spread per UK Region",
            color_discrete_map=REGION_COLS)
        show(fig_box, 320)

    # Workshop table
    st.subheader("Workshop Recommendations — Step D Output")
    reg_f = st.selectbox(
        "Filter by region:",
        ["All", "England", "Scotland", "Wales", "Northern Ireland"])
    df_ds = df_d.copy()
    if reg_f != "All":
        rc = next((c for c in df_ds.columns
                   if "region" in c.lower()), None)
        if rc:
            df_ds = df_ds[df_ds[rc].astype(str)
                          .str.contains(reg_f, case=False, na=False)]
    if not df_ds.empty:
        st.dataframe(df_ds, use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Communication Gap", "10.0",  "England — maximum")
    c2.metric("Recommendations",   "20",    "5 per UK region")
    c3.metric("#1 All 4 Regions",  "Communication", "Top skill everywhere")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — GLOBAL COMPARISON
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "🌍 Global Comparison":
    st.title("🌍 Global Comparison")
    st.caption("UK vs 81 countries — fair skill share % · not raw counts")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("UK Global Rank",  "#4",     "By gaming listings")
    c2.metric("Communication",   "80/81",  "Countries demand it")
    c3.metric("UK Comm. Share",  "52.12%", "Ranks #1 globally")
    c4.metric("Most Similar",    "France", "0.96 cosine similarity")

    st.markdown("---")

    # Top countries
    st.subheader("Top Countries by Gaming Job Listings")
    ctries = [
        ("United States",5604,False),("India",2374,False),
        ("Canada",1914,False),("United Kingdom",1634,True),
        ("China",998,False),("Poland",867,False),
        ("Germany",575,False),("Japan",535,False),
        ("Australia",447,False),("France",442,False),
        ("Ukraine",428,False),("Spain",402,False),
        ("Sweden",387,False),("Romania",355,False),
        ("Singapore",293,False),
    ]
    df_ct = pd.DataFrame(ctries,
                         columns=["Country","Jobs","is_uk"])
    df_ct["Type"] = df_ct["is_uk"].map(
        {True:"United Kingdom", False:"Other"})
    fig_ct = px.bar(
        df_ct.sort_values("Jobs"),
        x="Jobs", y="Country", orientation="h",
        title="Top 15 Countries — Unique Gaming Job Listings",
        color="Type",
        color_discrete_map={"United Kingdom": TEAL, "Other": DIM})
    fig_ct.update_traces(texttemplate="%{x:,}",
                         textposition="outside")
    fig_ct.update_layout(legend_title="")
    show(fig_ct, 500)

    # Excel live explorer
    st.subheader("Skill Explorer — UK vs World")
    df_raw, excel_ok = load_excel()
    if df_raw is not None and excel_ok:
        try:
            df_g = df_raw[
                df_raw["Company Category"].astype(str).str.strip()
                == "Gaming Company"].copy()
            CITY_MAP = {
                "London":"United Kingdom","Manchester":"United Kingdom",
                "Bristol":"United Kingdom","Edinburgh":"United Kingdom",
                "Glasgow":"United Kingdom","Birmingham":"United Kingdom",
                "Leeds":"United Kingdom","Liverpool":"United Kingdom",
                "Brighton":"United Kingdom","Cambridge":"United Kingdom",
                "Oxford":"United Kingdom","Guildford":"United Kingdom",
                "Belfast":"United Kingdom","Cardiff":"United Kingdom",
                "UK":"United Kingdom","England":"United Kingdom",
                "Scotland":"United Kingdom","Wales":"United Kingdom",
                "Northern Ireland":"United Kingdom",
                "New York":"United States","San Francisco":"United States",
                "Seattle":"United States","Los Angeles":"United States",
                "Austin":"United States","Chicago":"United States",
                "USA":"United States","US":"United States",
                "Vancouver":"Canada","Toronto":"Canada","Montreal":"Canada",
                "Bengaluru":"India","Bangalore":"India","Mumbai":"India",
                "Berlin":"Germany","Munich":"Germany",
                "Warsaw":"Poland","Krakow":"Poland",
                "Sydney":"Australia","Melbourne":"Australia",
                "Paris":"France","Tokyo":"Japan","Kyiv":"Ukraine",
                "Amsterdam":"Netherlands","Stockholm":"Sweden",
            }
            df_g["Country"] = (df_g["Country"].astype(str).str.strip()
                               .replace(CITY_MAP))
            df_g = df_g.dropna(subset=["Country"])
            df_g = df_g[~df_g["Country"].str.lower()
                        .isin(["nan","remote","none",""])]
            df_g["Skills"] = (df_g["Skills"].astype(str)
                              .str.lower().str.strip())
            df_exp = (df_g.assign(Skills=df_g["Skills"].str.split(","))
                      .explode("Skills"))
            df_exp["Skills"] = df_exp["Skills"].str.strip()
            df_exp = df_exp[~df_exp["Skills"]
                            .isin(["","nan","game-texts"])]
            tot = df_exp.groupby("Country").size().reset_index(
                name="total")
            valid = tot[tot["total"] >= 50]["Country"].tolist()
            df_exp = df_exp[df_exp["Country"].isin(valid)]
            tot = tot[tot["Country"].isin(valid)]
            sc = (df_exp.groupby(["Country","Skills"]).size()
                  .reset_index(name="count")
                  .merge(tot, on="Country"))
            sc["share_pct"] = (sc["count"] / sc["total"] * 100).round(2)

            skill_in = st.text_input(
                "Search any skill:",
                value="communication",
                placeholder="communication · python · unity · cpp").strip().lower()

            if skill_in:
                sd = sc[sc["Skills"] == skill_in].sort_values(
                    "share_pct", ascending=False)
                if sd.empty:
                    st.warning(f"'{skill_in}' not found. Try: "
                               f"communication, python, unity, cpp")
                else:
                    top_sd = sd.head(15).copy()
                    top_sd["Type"] = top_sd["Country"].apply(
                        lambda x: "United Kingdom"
                        if x == "United Kingdom" else "Other")
                    fig_sk = px.bar(
                        top_sd,
                        x="share_pct", y="Country", orientation="h",
                        title=f"Top 15 Countries — Skill Share: {skill_in}",
                        labels={"share_pct":"Skill Share (%)"},
                        color="Type",
                        color_discrete_map={
                            "United Kingdom": TEAL, "Other": DIM})
                    fig_sk.update_traces(texttemplate="%{x:.1f}%",
                                         textposition="outside")
                    fig_sk.update_layout(
                        yaxis_categoryorder="total ascending",
                        legend_title="")
                    show(fig_sk, 480)

                    uk_row = sd[sd["Country"] == "United Kingdom"]
                    g_avg  = round(sd["share_pct"].mean(), 2)
                    if len(uk_row):
                        uk_sh   = uk_row["share_pct"].values[0]
                        uk_rank = list(sd["Country"].values).index(
                            "United Kingdom") + 1
                        s1, s2, s3 = st.columns(3)
                        s1.metric("UK Share",  f"{uk_sh:.1f}%")
                        s2.metric("UK Rank",   f"#{uk_rank}/{len(sd)}")
                        s3.metric("Global Avg",f"{g_avg:.1f}%")
        except Exception as ex:
            st.error(f"Could not process global data: {str(ex)[:200]}")
    else:
        st.warning("Add Updated_27_02_26_-_Kabilan.xlsx to the project "
                   "folder to enable the live skill explorer.")

    # Analysis 1 — UK vs Global
    st.subheader("UK vs Global — Ahead or Behind?")
    vs_d = [
        ("Talent Acquisition",18.73),("Storytelling",8.41),
        ("Team Management",8.22),("Unreal",7.41),("Maya",6.57),
        ("C++",6.35),("Real-Time VFX",4.61),
        ("CI/CD",-8.25),("Python",-6.86),("SQL",-5.68),
        ("Docker",-5.10),("Kubernetes",-4.43),
        ("Linux",-4.41),("AWS",-4.41),
    ]
    df_vs = pd.DataFrame(vs_d, columns=["Skill","Diff"])
    df_vs["Status"] = df_vs["Diff"].apply(
        lambda x: "UK Ahead" if x > 0 else "UK Behind")
    fig_vs = px.bar(
        df_vs.sort_values("Diff"),
        x="Diff", y="Skill", orientation="h",
        title="UK vs Global Average Skill Share (% difference)",
        color="Status",
        color_discrete_map={"UK Ahead": GREEN, "UK Behind": RED})
    fig_vs.add_vline(x=0, line_color="rgba(255,255,255,.2)")
    show(fig_vs, 480)

    # Analysis 2 — Universality
    st.subheader("Global Skill Universality")
    univ = [
        ("Communication",80),("Team Management",71),
        ("Problem Solving",70),("Quality Control",70),
        ("Agile Dev",69),("Excel",68),("Python",67),
        ("Cross-Functional",66),("CI/CD",64),("SQL",64),
        ("AWS",63),("Kubernetes",62),("Data Analytics",60),("GitHub",58),
    ]
    df_un = pd.DataFrame(
        univ, columns=["Skill","Countries"]).sort_values("Countries")
    df_un["Type"] = df_un["Skill"].apply(
        lambda x: "Communication" if x == "Communication" else "Other")
    fig_un = px.bar(
        df_un, x="Countries", y="Skill", orientation="h",
        title="Most Universal Gaming Skills — Countries Demanding Each",
        color="Type",
        color_discrete_map={"Communication": TEAL, "Other": DIM})
    show(fig_un, 480)
    st.info("🌐 Communication demanded in 80/81 countries — "
            "the most universal gaming skill on Earth.")

    # Analysis 3 — Similar countries
    st.subheader("Countries Most Similar to UK")
    sim = [("France",0.96),("Japan",0.95),("United States",0.94),
           ("Sweden",0.93),("Brazil",0.93),("Spain",0.93),
           ("Malta",0.92),("UAE",0.92),("South Korea",0.92),
           ("Netherlands",0.92)]
    df_sim = pd.DataFrame(
        sim, columns=["Country","Similarity"]).sort_values("Similarity")
    fig_sim = px.bar(
        df_sim, x="Similarity", y="Country", orientation="h",
        title="Countries with Most Similar Skill Profile to UK",
        color="Similarity",
        color_continuous_scale=[[0, DIM],[1, TEAL]])
    fig_sim.update_layout(coloraxis_showscale=False,
                          xaxis_range=[0.88, 1.0])
    show(fig_sim, 360)

    # Rankings table
    st.subheader("UK Skill Rankings vs Global")
    rnk = pd.DataFrame([
        ["Communication",     52.12,  1, 55.06,  1, "↑ Ahead"],
        ["Talent Acquisition",37.11,  2, 18.38,  4, "↑ Ahead"],
        ["Team Management",   33.67,  3, 25.45,  2, "↓ Behind"],
        ["Storytelling",      13.07,  6,  4.66, 37, "↑ Ahead"],
        ["Python",            12.99,  7, 19.85,  3, "↓ Behind"],
        ["C++",               12.71,  8,  6.36, 25, "↑ Ahead"],
        ["Unreal",            12.56,  9,  5.15, 31, "↑ Ahead"],
        ["CI/CD",              5.60, 18, 13.85,  6, "↓ Behind"],
    ], columns=["Skill","UK Share %","UK Rank",
                "Global Avg %","Global Rank","Trend"])
    st.dataframe(rnk, use_container_width=True, hide_index=True)

    st.success("🏆 UK world-class in creative skills — Storytelling +8.41%, "
               "Unreal +7.41%, C++ +6.35%. Behind on DevOps — "
               "CI/CD -8.25%, Python -6.86%. "
               "France, Japan and USA have the most similar profiles.")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5 — CV EVALUATOR
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "📄 CV Evaluator":
    st.title("📄 CV Evaluator")
    st.caption("Paste your CV · auto-extract skills · match UK gaming jobs · AI feedback")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.info("**📤 Upload CV**\nPaste or upload file")
    with c2:
        st.info("**🔍 Extract Skills**\nAuto-detect gaming skills")
    with c3:
        st.info("**📊 Match Jobs**\nvs 1,121 UK gaming jobs")
    with c4:
        st.info("**💡 AI Feedback**\nPersonalised advice")

    st.markdown("---")

    # Input
    method = st.radio(
        "Input method:",
        ["Paste CV text", "Upload PDF / TXT"],
        horizontal=True)
    cv_text = ""
    if method == "Paste CV text":
        cv_text = st.text_area(
            "Paste your full CV here:",
            height=260,
            placeholder="Include skills, experience, tools and education...\n\n"
                        "Example: I have 3 years Unity and C++ experience, "
                        "worked in agile teams using Jira and GitHub, "
                        "strong communication and problem-solving skills, "
                        "proficient in Python and SQL...")
    else:
        up = st.file_uploader(
            "Upload your CV:", type=["txt","pdf"])
        if up:
            if up.type == "text/plain":
                cv_text = up.read().decode("utf-8", errors="ignore")
            else:
                try:
                    import pdfplumber
                    with pdfplumber.open(io.BytesIO(up.read())) as pdf:
                        cv_text = "\n".join(
                            p.extract_text() or "" for p in pdf.pages)
                except ImportError:
                    try:
                        import PyPDF2
                        reader = PyPDF2.PdfReader(
                            io.BytesIO(up.read()))
                        cv_text = "\n".join(
                            pg.extract_text() or ""
                            for pg in reader.pages)
                    except ImportError:
                        st.warning("Run: pip install pdfplumber  "
                                   "— or paste text manually.")

    # API key
    api_key = ""
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        pass
    if not api_key:
        with st.expander("⚙️ Optional: Anthropic API Key (for AI feedback)"):
            api_key = st.text_input(
                "API key:", type="password",
                placeholder="sk-ant-...")
            st.caption("Free at console.anthropic.com  ·  "
                       "Or add ANTHROPIC_API_KEY to .streamlit/secrets.toml")

    # Skills reference
    GAMING_SKILLS = [
        "communication","team-management","talent-acquisition",
        "cross-functional","problem-solving","python","excel",
        "quality-control","cpp","c++","unity","unreal","storytelling",
        "agile-development","budget-management","maya","c#","ms-office",
        "real-time-vfx","photoshop","data-analytics","machine-learning",
        "java","sql","aws","azure","docker","kubernetes","linux",
        "git","github","jira","confluence","blender","houdini",
        "rendering","javascript","typescript","react","node",
        "mongodb","ci-cd","user-experience-ux","product-management",
        "salesforce","tableau","figma","html","css","microservices",
        "networking","timeline-management",
    ]
    JOB_CATS = {
        "Engineering & Dev":  ["cpp","c++","c#","python","java",
                                "javascript","typescript","unity","unreal",
                                "git","github","agile-development",
                                "ci-cd","docker","kubernetes"],
        "Art & Tech Art":     ["maya","photoshop","blender","houdini",
                                "real-time-vfx","rendering"],
        "Game Design":        ["unity","unreal","storytelling",
                                "problem-solving","communication",
                                "user-experience-ux"],
        "UI/UX":              ["figma","photoshop","javascript","html",
                                "css","communication","user-experience-ux"],
        "Data & Analytics":   ["python","sql","data-analytics",
                                "machine-learning","excel","aws",
                                "azure","tableau"],
        "Cloud & DevOps":     ["aws","azure","docker","kubernetes","linux",
                                "ci-cd","python","networking","microservices"],
        "HR & Recruiting":    ["talent-acquisition","communication",
                                "team-management","excel","ms-office"],
        "Marketing & Adv":    ["communication","storytelling",
                                "data-analytics","budget-management"],
        "Production":         ["agile-development","jira","confluence",
                                "team-management","communication",
                                "budget-management","timeline-management"],
        "Biz Dev & Sales":    ["communication","budget-management",
                                "cross-functional","salesforce"],
    }
    TOP_P = ["communication","team-management","python","cpp","c++",
             "unity","agile-development","problem-solving",
             "excel","talent-acquisition"]

    if st.button("🔍  Analyse My CV", use_container_width=True):
        if not cv_text.strip():
            st.warning("Please paste or upload your CV text first.")
        else:
            txt = cv_text.lower()

            # Extract
            found = []
            for sk in GAMING_SKILLS:
                variants = [sk, sk.replace("-"," "), cn(sk).lower()]
                if any(v in txt for v in variants) and sk not in found:
                    found.append(sk)

            miss = [s for s in TOP_P
                    if s not in found
                    and s.replace("-"," ") not in txt]

            # Scores
            scores = []
            for cat, skills in JOB_CATS.items():
                m = [s for s in skills if s in found]
                score = round(len(m) / len(skills) * 100, 1)
                scores.append((cat, score, len(m), len(skills)))
            scores.sort(key=lambda x: x[1], reverse=True)
            overall = round(len(found) / len(GAMING_SKILLS) * 100, 1)

            st.markdown("---")
            st.subheader("Your CV Analysis Results")

            # Result KPIs
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Skills Found",    str(len(found)),
                      f"of {len(GAMING_SKILLS)} tracked")
            c2.metric("Gaming Match",    f"{overall}%",
                      "Industry relevance")
            c3.metric("Best Job Fit",    scores[0][0][:15],
                      f"{scores[0][1]:.0f}% match")
            c4.metric("Priority Gaps",   str(len(miss)),
                      "Missing top skills")

            st.markdown("---")
            cl, cr = st.columns(2)

            with cl:
                st.subheader(f"Skills Found — {len(found)} detected")
                if found:
                    badges = " · ".join(f"**{cn(s)}**"
                                        for s in sorted(found))
                    st.success(badges)
                else:
                    st.warning("No gaming skills detected. "
                               "Add tools: Unity, Python, C++, "
                               "Unreal, Agile Development.")

                st.subheader("Missing High-Priority Skills")
                if miss:
                    st.error("Missing: " + " · ".join(
                        f"**{cn(s)}**" for s in miss))
                    st.caption("These are the most demanded skills "
                               "in UK gaming — add them to your CV.")
                else:
                    st.success("All high-priority skills present!")

            with cr:
                st.subheader("Job Category Match Scores")
                df_cm = pd.DataFrame(
                    [(c, s, m, t)
                     for c,s,m,t in scores],
                    columns=["Category","Score %",
                             "Matched","Total"]
                ).sort_values("Score %", ascending=True)
                fig_cm = px.bar(
                    df_cm, x="Score %", y="Category",
                    orientation="h",
                    title="CV Match per Job Category",
                    color="Score %",
                    color_continuous_scale=[
                        [0,RED],[0.4,AMBER],[1,GREEN]])
                fig_cm.update_traces(texttemplate="%{x:.0f}%",
                                     textposition="outside")
                fig_cm.update_layout(coloraxis_showscale=False)
                show(fig_cm, 380)

            # Top 3
            st.subheader("Top Job Recommendations")
            t1, t2, t3 = st.columns(3)
            for i, (cat, score, matched, total) in \
                    enumerate(scores[:3]):
                col = t1 if i == 0 else t2 if i == 1 else t3
                with col:
                    col.metric(cat, f"{score:.0f}%",
                               f"{matched}/{total} skills")

            # Advice
            st.markdown("---")
            if overall == 0:
                st.warning("No gaming skills detected. Add specific "
                           "tools: Unity, Python, C++, Unreal, "
                           "Agile Development.")
            elif overall >= 60:
                st.success(
                    f"Excellent gaming profile! Best fit: {scores[0][0]}. "
                    f"Add {cn(miss[0]) if miss else 'portfolio projects'} "
                    f"to reach senior roles.")
            elif overall >= 30:
                st.info(
                    f"Good foundation. Strengthen by adding "
                    f"{', '.join(cn(s) for s in miss[:3])} "
                    f"— these appear in the most UK gaming job ads.")
            else:
                st.warning(
                    f"Add more gaming-specific skills. Priorities: "
                    f"{', '.join(cn(s) for s in miss[:4])}. "
                    f"Consider SideFest workshops.")

            # Claude AI feedback
            st.subheader("AI-Powered Feedback — Claude")
            if not api_key:
                st.info("Add your Anthropic API key above to get "
                        "detailed AI feedback — strengths, improvement "
                        "tips and specific UK gaming job recommendations.")
            else:
                with st.spinner("Claude is analysing your CV…"):
                    try:
                        import anthropic
                        client = anthropic.Anthropic(
                            api_key=api_key.strip())
                        top_names  = ", ".join(
                            c for c,_,_,_ in scores[:3])
                        found_disp = ", ".join(
                            cn(s) for s in found[:15])
                        miss_disp  = ", ".join(cn(s) for s in miss)
                        prompt = (
                            f"You are a UK gaming industry careers advisor.\n"
                            f"Analyse this CV for the UK gaming industry.\n\n"
                            f"CV TEXT:\n{cv_text[:3000]}\n\n"
                            f"ANALYSIS:\n"
                            f"Skills found: {found_disp or 'None'}\n"
                            f"Missing priority skills: {miss_disp or 'None'}\n"
                            f"Best job matches: {top_names}\n"
                            f"Overall match: {overall}%\n\n"
                            f"Provide:\n"
                            f"1. Overall assessment (2 sentences)\n"
                            f"2. Top 3 strengths for UK gaming\n"
                            f"3. Top 3 CV improvements\n"
                            f"4. Best UK gaming companies or roles\n"
                            f"5. One career tip for the UK gaming market\n\n"
                            f"Be concise and specific."
                        )
                        msg = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=900,
                            messages=[{"role":"user",
                                       "content":prompt}])
                        st.success("Claude's Assessment")
                        st.write(msg.content[0].text)
                    except ImportError:
                        st.error("Run: pip install anthropic")
                    except Exception as ex:
                        st.error(f"API error: {str(ex)[:200]}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "UK Gaming Industry — Skill Intelligence Dashboard  ·  "
    "University of Leicester  ·  AI for Business Intelligence  ·  "
    "Kabilan · 2025  ·  Data: UK Gaming Job Listings · Jul–Oct 2025")
