"""
UK Gaming Industry — Skill Demand Analysis (Streamlit)
All charts built with Plotly from CSV/Excel only (no static images).
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

APP_DIR = Path(__file__).resolve().parent


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
            template="plotly_white",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1E293B", family="Arial", size=12),
            margin=dict(l=40, r=40, t=50, b=40),
            title_font=dict(color="#0F172A", size=14),
            colorway=DARK_COLOURS,
        )
    except Exception:
        pass
    try:
        fig.update_xaxes(
            gridcolor="#E2E8F0",
            linecolor="#CBD5E1",
            tickfont=dict(color="#475569"),
            title_font=dict(color="#475569"),
        )
        fig.update_yaxes(
            gridcolor="#E2E8F0",
            linecolor="#CBD5E1",
            tickfont=dict(color="#475569"),
            title_font=dict(color="#475569"),
        )
    except Exception:
        pass
    try:
        fig.update_layout(
            legend=dict(
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="#E2E8F0",
                font=dict(color="#334155"),
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


def tab_header() -> None:
    st.markdown("## 🎮 UK Gaming Industry — Skill Demand Analysis")
    st.markdown("*University of Leicester | AI for Business Intelligence | Kabilan*")
    st.markdown("---")


def animated_metric(label, value, prefix="", suffix="", color="#38BDF8"):
    st.markdown(
        f"""
    <div style="background:#0F172A;border:1px solid #1E3A5F;border-radius:10px;
                padding:20px;text-align:center;margin:4px;">
        <div style="font-size:30px;font-weight:700;color:{color};">
            {prefix}{value}{suffix}
        </div>
        <div style="font-size:12px;color:#64748B;margin-top:6px;">{label}</div>
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
def load_excel() -> pd.DataFrame:
    p = _find_file("Updated_27_02_26_-_Kabilan.xlsx")
    if not p:
        raise FileNotFoundError("Updated_27_02_26_-_Kabilan.xlsx")
    return pd.read_excel(p, sheet_name="Combined Data")


st.set_page_config(
    page_title="UK Gaming Industry — Skill Demand Analysis",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
/* ── Light professional theme (original) ── */
[data-testid="stSidebar"] {background-color: #0F1B2D;}
[data-testid="stSidebar"] * {color: #E5E7EB !important;}
.metric-card {background:#1A2535;border:1px solid #0D9488;border-radius:10px;padding:16px;text-align:center;}
.metric-value {font-size:28px;font-weight:bold;color:#5EEAD4;}
.metric-label {font-size:12px;color:#9CA3AF;}
.callout {background:#FFF7ED;border-left:4px solid #F59E0B;padding:12px 16px;border-radius:0 8px 8px 0;margin:10px 0;}
.high-priority {background-color:#FFF5F5;}
.badge {display:inline-block;background:#0D9488;color:white;padding:3px 10px;border-radius:12px;margin:3px;font-size:12px;}
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

with st.spinner("Loading global dataset — 27,898 rows..."):
    try:
        df_excel = load_excel()
    except FileNotFoundError as e:
        st.error(f"Required Excel not found: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error reading Excel: {e}")
        st.stop()

with st.sidebar:
    tab_choice = st.radio(
        "section",
        [
            "TAB 1 — UK Overview",
            "TAB 2 — Regional Analysis",
            "TAB 3 — AI Gap Analysis",
            "TAB 4 — Experience Analysis",
            "TAB 5 — Global Comparison",
        ],
        label_visibility="collapsed",
    )

    # Global filters removed (defaults keep app logic stable)
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
    st.subheader("UK Overview")

    # Basic metrics (pre-computed headline figures)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Jobs", "1,121")
    m2.metric("Unique Skills", "352")
    m3.metric("Total Skill Rows", "6,948")
    m4.metric("UK Regions", "4")

    # Clean step_a data before aggregations
    df = df_a.copy()
    if "Skills" in df.columns:
        df = df[df["Skills"] != "game-texts"]
        df = df[df["Skills"].astype(str).str.strip() != ""]
        df = df[df["Skills"].astype(str).str.lower() != "nan"]
    if "UK Region" in df.columns:
        df = df[df["UK Region"].astype(str).str.strip() != "Unknown"]

    st.markdown("---")
    st.markdown("### 📊 Job Demand Analysis — Skills vs Actual Job Ads")
    st.markdown("*How many unique job ads demand each skill — not just how many times it appears*")

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
        plotly_show(fig_demand)

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
        plotly_show(fig_coverage)

    st.info(
        "**Key insight:** Communication appears in **610 skill mentions** across "
        "**348 unique job ads** — meaning **31.0% of all UK gaming jobs** require "
        "communication skills. This is the highest coverage of any skill in the dataset. "
        "Unity appears in **133 mentions** across **68 unique job ads** (6.1% coverage) "
        "— confirming it is a specialist gaming-only skill."
    )

    st.markdown("---")
    st.markdown("### 🎯 Job Ads by Category")
    st.markdown("*How many job ads exist per job category across UK gaming companies*")

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
        plotly_show(fig_cat)

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
        plotly_show(fig_cat_pie)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total UK Gaming Job Ads", "1,121")
    with col2:
        st.metric("Largest Category", "Art & Tech Art (172)")
    with col3:
        st.metric("Most Technical", "Engineering & Dev (167)")
    with col4:
        st.metric("Communication is needed in", "31% of all jobs")

    st.markdown("---")
    st.markdown("### Skill deep dive — explore one skill")
    if "Activated Date" in df.columns and "UK Region" in df.columns and "Skills" in df.columns:
        skills_opts = sorted(df["Skills"].dropna().astype(str).str.strip().unique().tolist())
        if skills_opts:
            default_skill = (
                next((s for s in skills_opts if s.lower() == "communication"), skills_opts[0])
            )
            selected_skill = st.selectbox("Select a skill", skills_opts, index=skills_opts.index(default_skill))
        else:
            selected_skill = ""

        if selected_skill:
            sub = df[df["Skills"].astype(str).str.strip().str.lower() == str(selected_skill).strip().lower()].copy()
            d = pd.to_datetime(sub["Activated Date"], errors="coerce")
            sub = sub.assign(_date=d).dropna(subset=["_date"])

            if not sub.empty:
                weekly = sub.set_index("_date").resample("W").size().rename("Count").reset_index()
                fig_trend = px.line(weekly, x="_date", y="Count", markers=True, title=f"Weekly trend — {selected_skill}")
                left, right = st.columns(2)
                with left:
                    plotly_show(fig_trend, height=420)

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
                    plotly_show(fig_reg, height=420)
            else:
                st.info("No rows for this skill under current filters.")
    else:
        st.caption("Skill deep dive unavailable (missing Activated Date / UK Region / Skills columns).")


def show_tab2(df_b: pd.DataFrame) -> None:
    st.subheader("Regional Analysis")

    reg_col = "UK Region"
    sk_col = "Skills"
    df_b2 = df_b.copy()

    regions = ["England", "Scotland", "Wales", "Northern Ireland"]
    st.markdown("### Controls")
    top_n = st.slider("Top skills to show (heatmap)", min_value=10, max_value=30, value=15, step=5)
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
            y=top_union,
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
        plotly_show(fig_hm, height=500)
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
    plotly_show(fig_stack, height=520)

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

    region_pick = st.selectbox("Filter region — top 10 skills", regions)
    sub_r = df_b2[df_b2[reg_col] == region_pick]
    top10r = sub_r[sk_col].astype(str).str.strip().value_counts().head(10).reset_index()
    top10r.columns = ["Skill", "Count"]
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
    plotly_show(fig_r)


def show_tab3(df_c: pd.DataFrame, df_d: pd.DataFrame) -> None:
    st.subheader("AI Gap Analysis")

    st.markdown("### Controls")
    regions_o = ["England", "Scotland", "Wales", "Northern Ireland"]
    region_view = st.selectbox("Region (for scatter + recommendations)", ["All"] + regions_o, index=0)
    min_demand = st.slider("Minimum demand (scatter/recs)", min_value=0, max_value=600, value=0, step=10)
    prio_view = st.multiselect("Priorities", options=["HIGH", "MED", "STD"], default=["HIGH", "MED", "STD"])

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown("#### Step A: Data Prep")
        st.write("6,948 rows, 352 skills, one skill per row")
    with s2:
        st.markdown("#### Step B: K-Means AI")
        st.write("TF-IDF converts skills to numbers, 6 clusters found")
    with s3:
        st.markdown("#### Step C: Gap Scoring")
        st.write("Location Quotient formula, 520 gap scores")
    with s4:
        st.markdown("#### Step D: Recommender")
        st.write("Top 5 per region, 20 total recommendations")

    dfc = df_c.copy()
    if region_view != "All" and "UK Region" in dfc.columns:
        dfc = dfc[dfc["UK Region"].astype(str).str.strip() == region_view]

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
    plotly_show(fig_gap, height=520)

    scatter_src = dfc.copy()
    if "Demand" in scatter_src.columns:
        scatter_src = scatter_src[pd.to_numeric(scatter_src["Demand"], errors="coerce").fillna(0) >= float(min_demand)]

    fig_sc = px.scatter(
        scatter_src,
        x="Demand",
        y="Gap_Score",
        color="Cluster_Name",
        size="Demand",
        hover_name="Skills",
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
        plotly_show(fig_sc, height=_gap_scatter_h)
    with col_box:
        plotly_show(fig_box, height=_gap_scatter_h)

    st.markdown("### Workshop recommendations")

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

    st.dataframe(df_show, use_container_width=True, hide_index=True, height=360)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Communication gap", "10.0")
    k2.metric("England top skills", "3 HIGH")
    k3.metric("Total recommendations", "20")
    k4.metric("#1 skill (all regions)", "Communication")
    k5.metric("Max demand", "527")


def show_tab4(df_xl: pd.DataFrame) -> None:
    st.subheader("Experience Analysis")

    df_uk = df_xl.copy()
    df_uk["Company Category"] = df_uk["Company Category"].astype(str).str.strip()
    df_uk = df_uk[
        (df_uk["Country"].astype(str).str.strip() == "United Kingdom")
        & (df_uk["Company Category"] == "Gaming Company")
    ].copy()

    def bucket_exp(x) -> str:
        if pd.isna(x):
            return "Unknown"
        try:
            v = float(x)
        except (TypeError, ValueError):
            return "Unknown"
        if v == 0:
            return "Entry Level (0 yrs)"
        if 1 <= v <= 2:
            return "Junior (1-2 yrs)"
        if 3 <= v <= 5:
            return "Mid-Level (3-5 yrs)"
        if 6 <= v <= 8:
            return "Senior (6-8 yrs)"
        if v >= 9:
            return "Expert (9+ yrs)"
        return "Unknown"

    if "Min Experience" in df_uk.columns:
        df_uk["ExpBucket"] = df_uk["Min Experience"].map(bucket_exp)
    else:
        df_uk["ExpBucket"] = "Unknown"

    t_ov, t_deep = st.tabs(["Overview", "Deep Analysis"])

    with t_ov:
        vc = df_uk["ExpBucket"].value_counts()
        fig_pie_e = px.pie(
            values=vc.values,
            names=vc.index,
            title="Experience level breakdown (UK Gaming)",
            hole=0.35,
        )
        plotly_show(fig_pie_e)

        job_cat = "Overall Job Category"
        if job_cat in df_uk.columns and "Min Experience" in df_uk.columns:
            sub_avg = df_uk[df_uk["Min Experience"].notna()].copy()
            top8 = (
                sub_avg.groupby(job_cat, dropna=False)["Min Experience"]
                .mean()
                .sort_values(ascending=False)
                .head(8)
                .reset_index()
            )
            top8.columns = ["Category", "Avg Min Experience"]
            fig_hbar = px.bar(
                top8.sort_values("Avg Min Experience", ascending=True),
                x="Avg Min Experience",
                y="Category",
                orientation="h",
                color_discrete_sequence=DARK_COLOURS,
                title="Average Min Experience by job category (top 8)",
            )
            plotly_show(fig_hbar)

        st_col = "State"
        if st_col in df_uk.columns:
            df_uk["Entry"] = (df_uk["ExpBucket"] == "Entry Level (0 yrs)").astype(int)
            df_uk["Mid"] = (df_uk["ExpBucket"] == "Mid-Level (3-5 yrs)").astype(int)
            df_uk["Senior"] = (df_uk["ExpBucket"] == "Senior (6-8 yrs)").astype(int)
            agg = df_uk.groupby(st_col, dropna=False)[["Entry", "Mid", "Senior"]].sum().reset_index()
            agg_m = agg.melt(id_vars=[st_col], var_name="Level", value_name="Count")
            fig_g = px.bar(
                agg_m,
                x=st_col,
                y="Count",
                color="Level",
                barmode="group",
                title="Entry / Mid-Level / Senior counts per UK region (State)",
                color_discrete_map={"Entry": COLOURS["green"], "Mid": COLOURS["amber"], "Senior": COLOURS["purple"]},
            )
            plotly_show(fig_g)

        e1, e2, e3, e4 = st.columns(4)
        e1.metric("No exp stated", "669 jobs (59.7%)")
        e2.metric("Mid-level", "251 jobs (55.5%)")
        e3.metric("Entry level", "27 (6.0%)")
        e4.metric("HR & Recruiting avg", "8.2 yrs")

    with t_deep:
        skcol = "Skills"
        if skcol not in df_uk.columns:
            st.error("Skills column missing in Excel.")
        else:

            def split_skills(s) -> list[str]:
                if pd.isna(s):
                    return []
                parts = str(s).split(",")
                out = []
                for p in parts:
                    t = p.strip().lower()
                    if t and t != "game-texts" and t != "nan":
                        out.append(t)
                return out

            df_uk["_skills_list"] = df_uk[skcol].map(split_skills)
            exp_simple = df_uk["ExpBucket"].map(
                {
                    "Entry Level (0 yrs)": "Entry",
                    "Junior (1-2 yrs)": "Junior",
                    "Mid-Level (3-5 yrs)": "Mid",
                    "Senior (6-8 yrs)": "Senior",
                    "Expert (9+ yrs)": "Expert",
                    "Unknown": np.nan,
                }
            )
            tmp = (
                df_uk.assign(_exp=exp_simple)
                .explode("_skills_list")
                .reset_index(drop=True)
            )
            tmp = tmp[tmp["_exp"].notna() & tmp["_skills_list"].notna()]

            skill_tot = tmp["_skills_list"].value_counts().head(15).index.tolist()
            levels = ["Entry", "Junior", "Mid", "Senior", "Expert"]
            heat = []
            for sk in skill_tot:
                row = []
                for lv in levels:
                    row.append(
                        len(tmp[(tmp["_skills_list"] == sk) & (tmp["_exp"] == lv)])
                    )
                heat.append(row)
            fig_heat = go.Figure(
                data=go.Heatmap(
                    z=heat,
                    x=levels,
                    y=skill_tot,
                    colorscale="YlOrRd",
                    colorbar=dict(title="Count"),
                )
            )
            fig_heat.update_layout(
                title="Top 15 skills vs experience level (counts)",
                yaxis=dict(autorange="reversed"),
            )
            plotly_show(fig_heat, height=520)

            seven = [
                "communication",
                "team-management",
                "talent-acquisition",
                "cross-functional",
                "python",
                "unity",
                "cpp",
            ]
            sub7 = tmp[tmp["_skills_list"].isin(seven)].copy()
            cts = (
                sub7.groupby(["_skills_list", "_exp"], as_index=False)
                .size()
                .rename(columns={"size": "Count", "_skills_list": "Skill", "_exp": "Level"})
            )
            fig_7 = px.bar(
                cts,
                x="Skill",
                y="Count",
                color="Level",
                barmode="group",
                category_orders={"Skill": seven, "Level": levels},
                color_discrete_sequence=DARK_COLOURS,
                title="Seven key skills by experience level",
            )
            plotly_show(fig_7, height=520)

            exp_summary = pd.DataFrame(
                {
                    "Skill": [
                        "Communication",
                        "Team Management",
                        "Talent Acquisition",
                        "Cross-Functional",
                        "Python",
                        "Unity",
                        "C++",
                    ],
                    "Entry Level": [16, 8, 10, 0, 9, 0, 3],
                    "Junior": [31, 19, 21, 6, 7, 3, 11],
                    "Mid-Level": [147, 103, 71, 50, 29, 34, 35],
                    "Senior": [29, 26, 18, 19, 5, 5, 6],
                    "Expert": [15, 25, 20, 12, 5, 11, 10],
                }
            )
            st.dataframe(exp_summary, use_container_width=True, hide_index=True, height=260)

            st.markdown(
                """
<div class="callout">
Communication has 9.2× more mid-level jobs than entry level. Team Management has 12.9× more.
SideFest needs a 3–5 year structured pathway.
</div>
""",
                unsafe_allow_html=True,
            )

            badges = [
                "agile-development",
                "aws",
                "azure",
                "c#",
                "ci-cd",
                "communication",
                "cpp",
                "data-analytics",
                "data-science",
                "excel",
                "github",
                "java",
                "kubernetes",
                "linux",
                "machine-learning",
                "ms-office",
                "problem-solving",
                "python",
                "quality-control",
                "salesforce",
                "sql",
                "storytelling",
                "talent-acquisition",
                "team-management",
                "timeline-management",
                "user-experience-ux",
            ]
            st.markdown("### Universal skills (26)")
            st.markdown("".join([f'<span class="badge">{b}</span>' for b in badges]), unsafe_allow_html=True)


def show_tab5() -> None:
    st.markdown(
        """
    <div class='callout'>
    This comparison uses <b>skill share percentage</b> — the proportion of each country's gaming jobs
    that demand a skill. This removes bias from larger countries having more jobs.
    A country with 10% share means 1 in 10 of their gaming jobs demands that skill.
    </div>
    """,
        unsafe_allow_html=True,
    )

    with st.spinner("Loading global dataset — 27,898 rows..."):
        df_raw = load_excel()

    city_to_country = {
        "Bengaluru": "India",
        "Bangalore": "India",
        "Mumbai": "India",
        "Delhi": "India",
        "New Delhi": "India",
        "Hyderabad": "India",
        "Pune": "India",
        "Chennai": "India",
        "Kolkata": "India",
        "Noida": "India",
        "Gurgaon": "India",
        "Gurugram": "India",
        "London": "United Kingdom",
        "Manchester": "United Kingdom",
        "Bristol": "United Kingdom",
        "Birmingham": "United Kingdom",
        "Edinburgh": "United Kingdom",
        "Glasgow": "United Kingdom",
        "Leeds": "United Kingdom",
        "Liverpool": "United Kingdom",
        "Brighton": "United Kingdom",
        "Cambridge": "United Kingdom",
        "Oxford": "United Kingdom",
        "Guildford": "United Kingdom",
        "England": "United Kingdom",
        "Scotland": "United Kingdom",
        "Wales": "United Kingdom",
        "Northern Ireland": "United Kingdom",
        "UK": "United Kingdom",
        "Britain": "United Kingdom",
        "El Segundo": "United States",
        "Los Angeles": "United States",
        "San Francisco": "United States",
        "Seattle": "United States",
        "New York": "United States",
        "Austin": "United States",
        "Chicago": "United States",
        "Boston": "United States",
        "Philadelphia": "United States",
        "San Diego": "United States",
        "Salt Lake City": "United States",
        "Washington": "United States",
        "Houston": "United States",
        "Dallas": "United States",
        "Atlanta": "United States",
        "Portland": "United States",
        "San Carlos": "United States",
        "St. Louis": "United States",
        "Denver": "United States",
        "Phoenix": "United States",
        "Las Vegas": "United States",
        "Miami": "United States",
        "Minneapolis": "United States",
        "Nashville": "United States",
        "Redwood City": "United States",
        "Irvine": "United States",
        "Bellevue": "United States",
        "Kirkland": "United States",
        "San Jose": "United States",
        "Sacramento": "United States",
        "USA": "United States",
        "US": "United States",
        "United States of America": "United States",
        "Vancouver": "Canada",
        "Toronto": "Canada",
        "Montreal": "Canada",
        "Calgary": "Canada",
        "Ottawa": "Canada",
        "Edmonton": "Canada",
        "Victoria": "Canada",
        "Waterloo": "Canada",
        "Shanghai": "China",
        "Beijing": "China",
        "Shenzhen": "China",
        "Guangzhou": "China",
        "Chengdu": "China",
        "Hangzhou": "China",
        "Berlin": "Germany",
        "Munich": "Germany",
        "Hamburg": "Germany",
        "Dusseldorf": "Germany",
        "Düsseldorf": "Germany",
        "Frankfurt": "Germany",
        "Cologne": "Germany",
        "Köln": "Germany",
        "Stuttgart": "Germany",
        "Warsaw": "Poland",
        "Krakow": "Poland",
        "Wroclaw": "Poland",
        "Gdansk": "Poland",
        "Poznan": "Poland",
        "Lodz": "Poland",
        "Sydney": "Australia",
        "Melbourne": "Australia",
        "Brisbane": "Australia",
        "Perth": "Australia",
        "Adelaide": "Australia",
        "Canberra": "Australia",
        "Paris": "France",
        "Lyon": "France",
        "Bordeaux": "France",
        "Montpellier": "France",
        "Toulouse": "France",
        "Madrid": "Spain",
        "Barcelona": "Spain",
        "Valencia": "Spain",
        "Seville": "Spain",
        "Bilbao": "Spain",
        "Kiev": "Ukraine",
        "Kyiv": "Ukraine",
        "Kharkiv": "Ukraine",
        "Dnipro": "Ukraine",
        "Odessa": "Ukraine",
        "Moscow": "Russia",
        "Saint Petersburg": "Russia",
        "St. Petersburg": "Russia",
        "Novosibirsk": "Russia",
        "Amsterdam": "Netherlands",
        "Rotterdam": "Netherlands",
        "Utrecht": "Netherlands",
        "The Hague": "Netherlands",
        "Stockholm": "Sweden",
        "Gothenburg": "Sweden",
        "Malmö": "Sweden",
        "Malmo": "Sweden",
        "Uppsala": "Sweden",
        "Tokyo": "Japan",
        "Osaka": "Japan",
        "Kyoto": "Japan",
        "Seoul": "South Korea",
        "Busan": "South Korea",
        "Taipei": "Taiwan",
        "Oslo": "Norway",
        "Copenhagen": "Denmark",
        "Zurich": "Switzerland",
        "Geneva": "Switzerland",
        "Vienna": "Austria",
        "Lisbon": "Portugal",
        "Porto": "Portugal",
        "Budapest": "Hungary",
        "Prague": "Czech Republic",
        "Brno": "Czech Republic",
        "Bucharest": "Romania",
        "Cluj": "Romania",
        "Belgrade": "Serbia",
        "Zagreb": "Croatia",
        "Ljubljana": "Slovenia",
        "Sofia": "Bulgaria",
        "Vilnius": "Lithuania",
        "Riga": "Latvia",
        "Tallinn": "Estonia",
        "Helsinki": "Finland",
        "Espoo": "Finland",
        "Ankara": "Turkey",
        "Istanbul": "Turkey",
        "Tel Aviv": "Israel",
        "Jerusalem": "Israel",
        "Dubai": "United Arab Emirates",
        "Abu Dhabi": "United Arab Emirates",
        "São Paulo": "Brazil",
        "Sao Paulo": "Brazil",
        "Rio de Janeiro": "Brazil",
        "Mexico City": "Mexico",
        "Guadalajara": "Mexico",
        "Buenos Aires": "Argentina",
        "Bogota": "Colombia",
        "Medellin": "Colombia",
        "Santiago": "Chile",
        "Lima": "Peru",
        "Johannesburg": "South Africa",
        "Cape Town": "South Africa",
        "Nairobi": "Kenya",
        "Lagos": "Nigeria",
        "Cairo": "Egypt",
        "Accra": "Ghana",
        "Shah Alam": "Malaysia",
        "Kuala Lumpur": "Malaysia",
        "Singapore City": "Singapore",
        "Jakarta": "Indonesia",
        "Bangkok": "Thailand",
        "Ho Chi Minh City": "Vietnam",
        "Hanoi": "Vietnam",
        "Manila": "Philippines",
        "Bratislava": "Slovakia",
        "Minsk": "Belarus",
        "Skopje": "North Macedonia",
        "Sarajevo": "Bosnia and Herzegovina",
    }
    city_map_ci = {str(k).strip().lower(): v for k, v in city_to_country.items()}

    df_global = df_raw[df_raw["Company Category"].astype(str).str.strip() == "Gaming Company"].copy()
    st.caption(f"Gaming Company rows before cleaning: {len(df_global):,}")

    df_global = df_global.dropna(subset=["Country"])
    df_global["Country"] = df_global["Country"].astype(str).str.strip()
    df_global = df_global[df_global["Country"] != ""]
    df_global = df_global[df_global["Country"].str.lower() != "nan"]
    df_global = df_global[df_global["Country"].str.lower() != "none"]

    df_global["Country"] = df_global["Country"].apply(
        lambda x: city_map_ci.get(str(x).strip().lower(), x)
    )

    df_global["Country"] = df_global["Country"].apply(
        lambda x: "United States"
        if str(x).strip() in ["US", "USA", "U.S.A", "U.S.", "United States of America"]
        else x
    )
    df_global["Country"] = df_global["Country"].apply(
        lambda x: "United Kingdom"
        if str(x).strip()
        in ["UK", "Britain", "Great Britain", "England", "Scotland", "Wales", "Northern Ireland"]
        else x
    )

    st.caption(f"Gaming Company rows after cleaning: {len(df_global):,}")

    df_global["Skills"] = df_global["Skills"].astype(str).str.lower().str.strip()
    df_exploded = df_global.assign(Skills=df_global["Skills"].str.split(",")).explode("Skills")
    df_exploded = df_exploded.reset_index(drop=True)
    df_exploded["Skills"] = df_exploded["Skills"].str.strip()
    df_exploded = df_exploded[df_exploded["Skills"] != ""]
    df_exploded = df_exploded[df_exploded["Skills"] != "nan"]
    df_exploded = df_exploded[df_exploded["Skills"] != "game-texts"]
    df_exploded = df_exploded.dropna(subset=["Skills", "Country"])

    total_per_country = df_exploded.groupby("Country").size().reset_index(name="total_rows")

    valid_countries = total_per_country[total_per_country["total_rows"] >= 100]["Country"].tolist()
    df_exploded = df_exploded[df_exploded["Country"].isin(valid_countries)]
    total_per_country = total_per_country[total_per_country["Country"].isin(valid_countries)]

    skill_country = df_exploded.groupby(["Country", "Skills"]).size().reset_index(name="count")
    skill_country = skill_country.merge(total_per_country, on="Country")
    skill_country["share_pct"] = (skill_country["count"] / skill_country["total_rows"] * 100).round(2)

    st.caption(f"Valid countries (100+ skill rows): {len(valid_countries)}")

    # Count UNIQUE JOB LISTINGS per country — not skill rows
    job_counts = df_global["Country"].value_counts().reset_index()
    job_counts.columns = ["Country", "Job_Listings"]
    job_counts = job_counts.head(15)
    job_counts["highlight"] = job_counts["Country"].apply(
        lambda x: "United Kingdom" if x == "United Kingdom" else "Other"
    )

    st.markdown("### 🌐 Top Countries by Gaming Job Listings")
    st.caption("Counting unique job listings per country — not skill rows")

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
    plotly_show(fig_countries)

    # Show summary metrics below chart
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Global Gaming Jobs", f"{len(df_global):,}")
    with col2:
        st.metric("Countries with Gaming Jobs", f"{df_global['Country'].nunique():,}")
    with col3:
        uk_jobs = len(df_global[df_global["Country"] == "United Kingdom"])
        uk_pct = round(uk_jobs / len(df_global) * 100, 1) if len(df_global) else 0.0
        st.metric("UK Share of Global Jobs", f"{uk_pct}%")

    st.markdown("---")

    st.markdown("### 🔍 Skill Explorer — Search Any Skill")
    skill_input = st.text_input(
        "Type a skill name:",
        value="communication",
        placeholder="e.g. communication, python, unity, c++",
    ).strip().lower()

    if skill_input:
        skill_data = skill_country[skill_country["Skills"] == skill_input].copy()
        skill_data = skill_data.sort_values("share_pct", ascending=False)

        if len(skill_data) == 0:
            st.warning(
                f"Skill '{skill_input}' not found. Try: communication, python, unity, team-management, cpp"
            )
        else:
            top15 = skill_data.head(15).copy()
            top15["highlight"] = top15["Country"].apply(
                lambda x: "United Kingdom" if x == "United Kingdom" else "Other"
            )

            fig_skill = px.bar(
                top15,
                x="share_pct",
                y="Country",
                orientation="h",
                color="highlight",
                color_discrete_map={"United Kingdom": "#EF4444", "Other": "#0D9488"},
                title=f"Top 15 Countries by Skill Share — {skill_input}",
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
            plotly_show(fig_skill)

            uk_row = skill_data[skill_data["Country"] == "United Kingdom"]
            n_countries = len(skill_data)
            global_avg = float(skill_data["share_pct"].mean())
            global_avg_r = round(global_avg, 2)

            col1, col2, col3 = st.columns(3)
            if len(uk_row) > 0:
                uk_share = float(uk_row["share_pct"].values[0])
                skill_ranked = skill_data.sort_values("share_pct", ascending=False).reset_index(drop=True)
                skill_ranked["rank"] = np.arange(1, len(skill_ranked) + 1)
                uk_r = skill_ranked[skill_ranked["Country"] == "United Kingdom"]
                uk_rank_num = int(uk_r["rank"].iloc[0]) if not uk_r.empty else "N/A"
                diff = round(uk_share - global_avg_r, 2)
                direction = "above" if diff >= 0 else "below"
                diff_abs = abs(diff)

                with col1:
                    st.metric("UK share %", f"{uk_share:.2f}%")
                with col2:
                    st.metric("UK rank", f"#{uk_rank_num} / {n_countries}")
                with col3:
                    st.metric("Global avg share %", f"{global_avg_r:.2f}%")

                st.info(
                    f"**'{skill_input}'** is demanded in **{n_countries} countries** globally. "
                    f"UK skill share is **{uk_share:.2f}%**. "
                    f"The global average is **{global_avg_r:.2f}%**. "
                    f"The UK is **{direction}** the global average by **{diff_abs:.2f}%**."
                )
            else:
                with col1:
                    st.metric("UK share %", "Not in top countries")
                with col2:
                    st.metric("UK rank", f"N/A / {n_countries}")
                with col3:
                    st.metric("Global avg share %", f"{global_avg_r:.2f}%")
                st.warning(f"United Kingdom does not appear in the data for '{skill_input}'.")

    st.markdown("---")

    st.markdown("### 📊 UK Skill Rankings vs Global Rankings")
    st.markdown("*Which skills is the UK ahead of or behind the world on?*")

    uk_skills = skill_country[skill_country["Country"] == "United Kingdom"].copy()
    uk_skills = uk_skills.sort_values("share_pct", ascending=False).head(20)
    uk_skills = uk_skills.rename(columns={"share_pct": "uk_share"})

    global_avg_skills = skill_country.groupby("Skills")["share_pct"].mean().reset_index()
    global_avg_skills.columns = ["Skills", "global_share"]
    global_avg_skills = global_avg_skills.sort_values("global_share", ascending=False)
    global_avg_skills["global_rank"] = range(1, len(global_avg_skills) + 1)

    uk_skills["uk_rank"] = range(1, len(uk_skills) + 1)
    comparison = uk_skills[["Skills", "uk_share", "uk_rank"]].merge(
        global_avg_skills[["Skills", "global_share", "global_rank"]],
        on="Skills",
        how="left",
    )
    comparison["uk_share"] = comparison["uk_share"].round(2)
    comparison["global_share"] = comparison["global_share"].round(2)
    comparison["Trend"] = comparison.apply(
        lambda row: "↑ Ahead" if row["uk_rank"] <= row["global_rank"] else "↓ Behind",
        axis=1,
    )
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

    st.markdown(
        """
    <div class='callout'>
    <b>What this means for SideFest:</b><br>
    Skills where the UK ranks <b>above the global average (↑ Ahead)</b> are strong assets —
    UK young people trained in these skills are globally competitive.<br><br>
    Skills where the UK ranks <b>below the global average (↓ Behind)</b> represent future
    opportunities — the UK gaming industry has not yet fully developed these skills,
    making them valuable to teach now before demand catches up.
    </div>
    """,
        unsafe_allow_html=True,
    )


if tab_choice == "TAB 1 — UK Overview":
    show_tab1(df_a)
elif tab_choice == "TAB 2 — Regional Analysis":
    show_tab2(df_b)
elif tab_choice == "TAB 3 — AI Gap Analysis":
    show_tab3(df_c, df_d)
elif tab_choice == "TAB 4 — Experience Analysis":
    show_tab4(df_excel)
elif tab_choice == "TAB 5 — Global Comparison":
    show_tab5()

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#9CA3AF;font-size:12px;'>"
    "University of Leicester | AI for Business Intelligence | Kabilan | 2025 | "
    "Data source: UK Gaming Job Listings Jul–Oct 2025"
    "</div>",
    unsafe_allow_html=True,
)
