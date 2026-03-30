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

CLUSTER_COLOURS = {
    "Game Development & Programming": "#1D4ED8",
    "Soft Skills & Business Development": "#6D28D9",
    "Project & Development Management": "#065F46",
    "Soft Skills & Creative Production": "#9D174D",
    "Business Tools & Productivity": "#92400E",
    "Cloud, Infrastructure & DevOps": "#0369A1",
}

REGION_COLOURS = {
    "England": "#1D4ED8",
    "Scotland": "#065F46",
    "Wales": "#92400E",
    "Northern Ireland": "#5B21B6",
}

POPULATION = {
    "England": 56490048,
    "Scotland": 5490000,
    "Wales": 3200000,
    "Northern Ireland": 1910000,
}

CITY_TO_COUNTRY = {
    "bengaluru": "India",
    "london": "United Kingdom",
    "vancouver": "Canada",
    "warsaw": "Poland",
    "shanghai": "China",
    "berlin": "Germany",
    "toronto": "Canada",
    "sydney": "Australia",
    "amsterdam": "Netherlands",
    "barcelona": "Spain",
    "kiev": "Ukraine",
    "kyiv": "Ukraine",
    "moscow": "Russia",
    "melbourne": "Australia",
    "mumbai": "India",
}


def apply_plotly_style(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", size=12, color="#1E293B"),
        margin=dict(l=20, r=20, t=40, b=20),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    return fig


def plotly_show(fig: go.Figure) -> None:
    apply_plotly_style(fig)
    st.plotly_chart(fig, use_container_width=True)


def tab_header() -> None:
    st.markdown("## 🎮 UK Gaming Industry — Skill Demand Analysis")
    st.markdown("*University of Leicester | AI for Business Intelligence | Kabilan*")
    st.markdown("---")


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
    st.markdown("## 🎮 Navigation")
    st.markdown("---")
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
    st.markdown("---")
    st.markdown("**TAB 1**: UK headline stats + top skills.")
    st.markdown("**TAB 2**: Regional skill demand + clusters (normalised /100k).")
    st.markdown("**TAB 3**: Stage A→D gap pipeline + workshop priorities.")
    st.markdown("**TAB 4**: Experience distribution + gap skills by level.")
    st.markdown("**TAB 5**: Fair global comparison using skill share (% of jobs).")
    st.markdown("---")
    st.markdown("University of Leicester")
    st.markdown("AI for Business Intelligence")
    st.markdown("Kabilan | 2025")


def show_tab1(df_a: pd.DataFrame) -> None:
    tab_header()
    st.subheader("UK Overview")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Jobs", "1,121")
    m2.metric("Unique Skills", "352")
    m3.metric("Total Skill Rows", "6,948")
    m4.metric("UK Regions", "4")

    skill_col = "Skills" if "Skills" in df_a.columns else df_a.columns[4]
    top20 = (
        df_a[skill_col]
        .astype(str)
        .str.strip()
        .value_counts()
        .head(20)
        .reset_index()
    )
    top20.columns = ["Skill", "Count"]
    fig1 = px.bar(
        top20.sort_values("Count", ascending=True),
        x="Count",
        y="Skill",
        orientation="h",
        color_discrete_sequence=[COLOURS["teal"]],
    )
    fig1.update_traces(hovertemplate="%{y}: %{x}<extra></extra>")
    fig1.update_layout(
        title="Top 20 Most Demanded Skills — UK Gaming Industry",
        xaxis_title="Count",
        yaxis_title="",
        showlegend=False,
    )
    plotly_show(fig1)

    pie_labels = [
        "Soft Skills",
        "Other",
        "Tools & Software",
        "Programming",
        "3D Art & Design",
        "Game Engines & Dev",
        "Cloud & DevOps",
    ]
    pie_vals = [2499, 1457, 893, 639, 575, 512, 373]
    fig_pie = go.Figure(
        data=[
            go.Pie(
                labels=pie_labels,
                values=pie_vals,
                hole=0.35,
                marker=dict(colors=px.colors.sequential.Teal_r[: len(pie_vals)]),
            )
        ]
    )
    fig_pie.update_layout(title="Skill category mix (reference distribution)")
    plotly_show(fig_pie)

    hierarchy = pd.DataFrame(
        {
            "Rank": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "Skill": [
                "Communication",
                "Team Management",
                "Talent Acquisition",
                "Cross-Functional",
                "Python",
                "Excel",
                "Quality-Control",
                "Problem-Solving",
                "Unity",
                "C++",
            ],
            "Gaming": ["560", "335", "317", "168", "134", "124", "124", "127", "122", "121"],
            "Tech": ["1,060", "696", "688", "396", "267", "302", "—", "233", "—", "—"],
            "Transferable": ["1,620", "1,031", "1,005", "564", "401", "421", "314", "360", "—", "—"],
            "Type": [
                "All 3 tiers",
                "All 3 tiers",
                "All 3 tiers",
                "All 3 tiers",
                "All 3 tiers",
                "All 3 tiers",
                "Gaming+Trans",
                "All 3 tiers",
                "Gaming ONLY",
                "Gaming ONLY",
            ],
        }
    )

    def _style_hierarchy(row: pd.Series) -> list[str]:
        skill = str(row["Skill"])
        if skill == "Communication":
            return ["background-color: #FEF3C7"] * len(row)
        if skill in ("Unity", "C++"):
            return ["background-color: #D1FAE5"] * len(row)
        return [""] * len(row)

    st.dataframe(
        hierarchy.style.apply(_style_hierarchy, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        """
<div class="callout">
<b>Insight</b><br/>
Communication leads ALL 3 tiers with 560 gaming posts, 1,060 tech posts and 1,620 transferable posts.
Unity and C++ are gaming-exclusive — they appear ONLY in gaming jobs.
</div>
""",
        unsafe_allow_html=True,
    )


def show_tab2(df_b: pd.DataFrame) -> None:
    tab_header()
    st.subheader("Regional Analysis")

    reg_col = "UK Region"
    sk_col = "Skills"
    df_b2 = df_b.copy()

    regions = ["England", "Scotland", "Wales", "Northern Ireland"]
    per_region_top: dict[str, pd.Series] = {}
    for r in regions:
        sub = df_b2[df_b2[reg_col] == r]
        per_region_top[r] = sub[sk_col].astype(str).str.strip().value_counts().head(15)

    top_union: list[str] = []
    for r in regions:
        for s in per_region_top[r].index:
            if s not in top_union:
                top_union.append(s)
            if len(top_union) >= 15:
                break
        if len(top_union) >= 15:
            break
    if len(top_union) < 15:
        for r in regions:
            for s in per_region_top[r].index:
                if s not in top_union:
                    top_union.append(s)
                if len(top_union) >= 15:
                    break
            if len(top_union) >= 15:
                break
    top_union = top_union[:15]

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
    plotly_show(fig_hm)

    st.markdown("### Regional top 5 (reference cards)")
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
    c1, c2, c3, c4 = st.columns(4)
    for col, reg in zip([c1, c2, c3, c4], regions):
        with col:
            st.markdown(
                f"#### <span style='color:{REGION_COLOURS.get(reg,'#333')}'>{reg}</span>",
                unsafe_allow_html=True,
            )
            for name, posts, norm in cards.get(reg, []):
                st.markdown(f"**{name}** — {posts} ({norm}/100k)")

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
        color_discrete_map=CLUSTER_COLOURS,
    )
    fig_stack.update_layout(barmode="stack", xaxis_title="", yaxis_title="Skills per 100k population")
    plotly_show(fig_stack)

    exact_tab2 = pd.DataFrame(
        [
            ("England", 3.55, 3.55, 1.49, 1.45, 0.72, 0.71),
            ("Scotland", 2.19, 1.60, 0.93, 0.44, 0.47, 0.18),
            ("Wales", 1.06, 0.47, 0.09, 0.16, 0.22, 0.28),
            ("N. Ireland", 1.88, 1.20, 0.58, 0.21, 0.37, 0.00),
        ],
        columns=["Region", "Game Dev", "Soft Skills", "Proj Mgmt", "Creative", "Biz Tools", "Cloud"],
    )
    st.dataframe(exact_tab2, use_container_width=True, hide_index=True)

    region_pick = st.selectbox("Filter region — top 10 skills", regions)
    sub_r = df_b2[df_b2[reg_col] == region_pick]
    top10r = sub_r[sk_col].astype(str).str.strip().value_counts().head(10).reset_index()
    top10r.columns = ["Skill", "Count"]
    fig_r = px.bar(
        top10r.sort_values("Count", ascending=True),
        x="Count",
        y="Skill",
        orientation="h",
        color_discrete_sequence=[REGION_COLOURS.get(region_pick, COLOURS["teal"])],
    )
    fig_r.update_layout(title=f"Top 10 skills — {region_pick}", showlegend=False)
    plotly_show(fig_r)


def show_tab3(df_c: pd.DataFrame, df_d: pd.DataFrame) -> None:
    tab_header()
    st.subheader("AI Gap Analysis")

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

    gap_avg = (
        df_c.groupby(["UK Region", "Cluster_Name"], as_index=False)["Gap_Score"]
        .mean()
        .rename(columns={"Gap_Score": "Avg Gap"})
    )
    regions_o = ["England", "Scotland", "Wales", "Northern Ireland"]
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
            colorscale="RdYlGn_r",
            colorbar=dict(title="Avg gap"),
        )
    )
    fig_gap.update_layout(
        title="Average Gap Score — Region × Skill Cluster",
        yaxis=dict(autorange="reversed"),
    )
    plotly_show(fig_gap)

    exact_gap = pd.DataFrame(
        [
            ("England", 5.07, 5.09, 5.09, 5.21, 5.26, 5.09),
            ("Scotland", 4.74, 4.25, 4.62, 4.82, 4.75, 4.82),
            ("Wales", 3.41, 3.50, 3.59, 4.18, 4.64, 4.66),
            ("N. Ireland", 2.77, 0.00, 3.90, 4.63, 4.52, 4.69),
        ],
        columns=["Region", "Biz Tools", "Cloud", "Game Dev", "Proj Mgmt", "Soft Skills", "Creative"],
    )
    st.dataframe(exact_gap, use_container_width=True, hide_index=True)

    eng = df_c[df_c["UK Region"].astype(str).str.strip() == "England"].copy()
    fig_sc = px.scatter(
        eng,
        x="Demand",
        y="Gap_Score",
        color="Cluster_Name",
        size="Demand",
        hover_name="Skills",
        color_discrete_map=CLUSTER_COLOURS,
        title="Demand vs Gap Score — England (each dot = one skill)",
    )
    plotly_show(fig_sc)

    fig_box = px.box(
        df_c,
        x="UK Region",
        y="Gap_Score",
        color="UK Region",
        color_discrete_map=REGION_COLOURS,
        title="Gap Score Distribution by UK Region",
    )
    plotly_show(fig_box)

    st.markdown("### Workshop recommendations")
    rec = df_d.copy()
    rec = rec.rename(
        columns={
            "UK_Region": "Region",
            "Priority_Rank": "Rank",
            "Skill_Cluster": "Cluster",
            "Demand_Count": "Demand",
        }
    )

    def _prio(x: str) -> str:
        s = str(x).upper()
        if "HIGH" in s:
            return "HIGH"
        if "MEDIUM" in s:
            return "MED"
        return "STD"

    if "Workshop_Recommendation" in rec.columns:
        rec["Priority"] = rec["Workshop_Recommendation"].map(_prio)
    else:
        rec["Priority"] = "STD"

    reg_opts = ["All"] + sorted(rec["Region"].dropna().unique().tolist()) if "Region" in rec.columns else ["All"]
    filt = st.selectbox("Region filter", reg_opts)
    df_show = rec if filt == "All" else rec[rec["Region"] == filt]

    def colour_priority(row: pd.Series) -> list[str]:
        pr = row.get("Priority", "")
        wr = str(row.get("Workshop_Recommendation", ""))
        if pr == "HIGH" or wr.startswith("🔴"):
            return ["background-color: #FFF5F5; color: #EF4444; font-weight: bold"] * len(row)
        if pr == "MED" or wr.startswith("🟠"):
            return ["background-color: #FFFBEB; color: #D97706; font-weight: bold"] * len(row)
        return ["background-color: #F0FFF4; color: #059669"] * len(row)

    st.dataframe(
        df_show.style.apply(colour_priority, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Communication gap", "10.0")
    k2.metric("England top skills", "3 HIGH")
    k3.metric("Total recommendations", "20")
    k4.metric("#1 skill (all regions)", "Communication")
    k5.metric("Max demand", "527")


def show_tab4(df_xl: pd.DataFrame) -> None:
    tab_header()
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
                color_discrete_sequence=[COLOURS["teal"]],
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
            plotly_show(fig_heat)

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
                color_discrete_sequence=px.colors.qualitative.Set2,
                title="Seven key skills by experience level",
            )
            plotly_show(fig_7)

            summary = pd.DataFrame(
                [
                    ("Communication", 16, 31, 147, 29, 15),
                    ("Team Management", 8, 19, 103, 26, 25),
                    ("Talent Acquisition", 10, 21, 71, 18, 20),
                    ("Cross-Functional", 0, 6, 50, 19, 12),
                    ("Python", 9, 7, 29, 5, 5),
                    ("Unity", 0, 3, 34, 5, 11),
                    ("C++", 3, 11, 35, 6, 10),
                ],
                columns=["Skill", "Entry", "Junior", "Mid", "Senior", "Expert"],
            )
            st.dataframe(summary, use_container_width=True, hide_index=True)

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


def show_tab5(df_xl: pd.DataFrame) -> None:
    tab_header()
    st.subheader("Global Comparison — UK vs World")

    st.markdown(
        """
This comparison uses **skill share percentage** — the proportion of each country's gaming jobs that demand a skill.
This removes bias from larger countries having more jobs. A country with 10% share means 1 in 10 of their gaming jobs demands that skill.
"""
    )

    g = df_xl.copy()
    g["Company Category"] = g["Company Category"].astype(str).str.strip()
    g = g[g["Company Category"] == "Gaming Company"].copy()

    st.caption(f"Gaming Company rows: {len(g):,}")

    if "City" in g.columns:

        def map_city(row) -> str:
            c = str(row.get("Country", "")).strip()
            city = str(row.get("City", "")).strip().lower()
            if city in CITY_TO_COUNTRY:
                return CITY_TO_COUNTRY[city]
            return c

        g["Country"] = g.apply(map_city, axis=1)

    def explode_skills(row) -> list[str]:
        s = row.get("Skills", "")
        if pd.isna(s):
            return []
        out = []
        for p in str(s).split(","):
            t = p.strip().lower()
            if t and t != "game-texts" and t != "nan":
                out.append(t)
        return out

    g["_sk"] = g.apply(explode_skills, axis=1)
    # explode duplicates index labels; reset so boolean row filtering works on all pandas versions
    global_skills = (
        g.explode("_sk").rename(columns={"_sk": "Skills"}).reset_index(drop=True)
    )
    global_skills = global_skills[global_skills["Skills"].notna()].copy()

    total_per_country = global_skills.groupby("Country").size()
    skill_country = global_skills.groupby(["Country", "Skills"], as_index=False).size().rename(
        columns={"size": "count"}
    )
    skill_country["total"] = skill_country["Country"].map(total_per_country)
    skill_country["share_pct"] = (skill_country["count"] / skill_country["total"] * 100).round(2)
    skill_country = skill_country[skill_country["total"] >= 50].copy()

    q = st.text_input("Skill search", value="communication").strip().lower()
    if not q:
        st.stop()

    sk_f = skill_country[skill_country["Skills"].str.contains(q, na=False, case=False)]
    if sk_f.empty:
        sk_f = skill_country[skill_country["Skills"].str.lower() == q]
    if sk_f.empty:
        st.warning("No matching skill in global data.")
        st.stop()

    top_skill = sk_f.groupby("Skills")["count"].sum().sort_values(ascending=False).index[0]
    one = sk_f[sk_f["Skills"] == top_skill].sort_values("share_pct", ascending=False)

    top15 = one.head(15).copy()
    top15["Highlight"] = top15["Country"].apply(
        lambda c: "United Kingdom" if "united kingdom" in str(c).lower() or str(c).strip().lower() == "uk" else "Other"
    )
    fig_b = px.bar(
        top15.sort_values("share_pct", ascending=True),
        x="share_pct",
        y="Country",
        orientation="h",
        color="Highlight",
        color_discrete_map={"United Kingdom": COLOURS["red"], "Other": COLOURS["teal"]},
        title=f"Top 15 countries by skill share — {top_skill}",
    )
    fig_b.update_traces(hovertemplate="%{y}: %{x}%<extra></extra>")
    plotly_show(fig_b)

    def _is_uk(s: str) -> bool:
        t = str(s).strip().lower()
        return "united kingdom" in t or t == "uk"

    one_sorted = one.sort_values("share_pct", ascending=False).reset_index(drop=True)
    one_sorted["Rank"] = np.arange(1, len(one_sorted) + 1)

    uk_rows = one_sorted[one_sorted["Country"].map(_is_uk)]
    uk_share = float(uk_rows.iloc[0]["share_pct"]) if not uk_rows.empty else float("nan")
    uk_rank = int(uk_rows.iloc[0]["Rank"]) if not uk_rows.empty else None

    n_countries = int(one["Country"].nunique())
    global_avg = float(one["share_pct"].mean())
    diff = (uk_share - global_avg) if uk_share == uk_share else 0.0
    above = "above" if (uk_share == uk_share and uk_share >= global_avg) else "below"

    c1, c2, c3 = st.columns(3)
    c1.metric("UK share %", f"{uk_share:.2f}%" if uk_share == uk_share else "N/A")
    c2.metric("UK rank", f"#{uk_rank} / {n_countries}" if uk_rank is not None else "N/A")
    c3.metric("Global avg share %", f"{global_avg:.2f}%")

    if uk_share == uk_share:
        st.info(
            f"'{top_skill}' is demanded in {n_countries} countries globally. "
            f"UK skill share is {uk_share:.2f}%. "
            f"The global average is {global_avg:.2f}%. "
            f"The UK is {above} the global average by {abs(diff):.2f}%."
        )
    else:
        st.info(
            f"'{top_skill}' is demanded in {n_countries} countries globally. "
            f"The global average is {global_avg:.2f}%."
        )

    st.markdown("### UK vs Global ranking (top 20 UK skills)")
    uk_only = global_skills[
        global_skills["Country"].astype(str).str.lower().str.contains("united kingdom")
        | (global_skills["Country"].astype(str).str.strip().str.lower() == "uk")
    ].copy()
    uk_tot = len(uk_only)
    if uk_tot == 0:
        st.warning("No UK rows for ranking table.")
    else:
        uk_counts = uk_only.groupby("Skills").size().rename("uk_n").sort_values(ascending=False)
        uk_top20 = uk_counts.head(20).reset_index()
        uk_top20["UK Share %"] = (uk_top20["uk_n"] / uk_tot * 100).round(4)
        uk_top20["UK Rank"] = uk_top20["UK Share %"].rank(method="min", ascending=False).astype(int)

        glob_tot = len(global_skills)
        glob_counts = global_skills.groupby("Skills").size()
        glob_share_all = (glob_counts / glob_tot * 100).rename("Global Share %").reset_index()
        glob_share_all["Global Rank"] = glob_share_all["Global Share %"].rank(method="min", ascending=False).astype(int)

        comp = uk_top20.merge(glob_share_all, on="Skills", how="left")
        comp["Trend"] = comp.apply(
            lambda r: "↑ Ahead"
            if pd.notna(r["Global Rank"]) and int(r["UK Rank"]) <= int(r["Global Rank"])
            else "↓ Behind",
            axis=1,
        )
        show_cols = ["Skills", "UK Share %", "UK Rank", "Global Share %", "Global Rank", "Trend"]
        comp = comp.rename(columns={"Skills": "Skill"})[show_cols]

        def _trend_style(row: pd.Series) -> list[str]:
            t = row.get("Trend", "")
            col = "#D1FAE5" if "Ahead" in str(t) else "#FEE2E2"
            return [f"background-color: {col}"] * len(row)

        st.dataframe(
            comp.style.apply(_trend_style, axis=1),
            use_container_width=True,
            hide_index=True,
        )

    country_totals = global_skills.groupby("Country").size().sort_values(ascending=False)
    top15c = country_totals.head(15).reset_index()
    top15c.columns = ["Country", "rows"]
    top15c["Highlight"] = top15c["Country"].apply(
        lambda c: "UK" if "united kingdom" in str(c).lower() else "Other"
    )
    fig_top = px.bar(
        top15c.sort_values("rows", ascending=True),
        x="rows",
        y="Country",
        orientation="h",
        color="Highlight",
        color_discrete_map={"UK": COLOURS["red"], "Other": COLOURS["teal"]},
        title="Top 15 Countries by Gaming Job Listings",
    )
    plotly_show(fig_top)

    st.markdown(
        """
<div class="callout">
Skills where UK ranks above the global average are strong assets for UK young people — these skills make them globally competitive.
Skills where UK ranks below the global average represent future opportunities the UK gaming industry has not yet fully developed.
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
    show_tab5(df_excel)

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#9CA3AF;font-size:12px;'>"
    "University of Leicester | AI for Business Intelligence | Kabilan | 2025 | "
    "Data source: UK Gaming Job Listings Jul–Oct 2025"
    "</div>",
    unsafe_allow_html=True,
)
