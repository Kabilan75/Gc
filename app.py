import math
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
except Exception:  # pragma: no cover
    px = None


APP_DIR = Path(__file__).resolve().parent


st.set_page_config(
    page_title="UK Gaming Industry — Skill Demand Analysis Dashboard",
    page_icon="🎮",
    layout="wide",
)


st.markdown(
    """
<style>
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #081a33 0%, #061427 100%);
    color: #ffffff;
  }
  [data-testid="stSidebar"] * { color: #ffffff; }
  .small-muted { color: rgba(255,255,255,0.75); font-size: 0.92rem; }
  .badge {
    display:inline-block; padding: 0.28rem 0.55rem; margin: 0.15rem 0.25rem 0.15rem 0;
    border-radius: 999px; border: 1px solid rgba(255,255,255,0.15);
    background: rgba(255,255,255,0.06); font-size: 0.9rem;
  }
  .callout {
    border-left: 5px solid #f97316; background: rgba(249,115,22,0.12);
    padding: 0.85rem 1rem; border-radius: 0.5rem;
  }
</style>
""",
    unsafe_allow_html=True,
)


def _candidate_paths(*filenames: str) -> list[Path]:
    # Include common folders + any first-level subfolder to make deployments
    # resilient to minor folder naming differences.
    search_dirs = [APP_DIR]
    for p in [
        APP_DIR / "Stage 3 Charts",
        APP_DIR / "expr charts",
        APP_DIR / "Step files",
    ]:
        search_dirs.append(p)
    try:
        for d in APP_DIR.iterdir():
            if d.is_dir():
                search_dirs.append(d)
    except Exception:  # pragma: no cover
        pass
    out: list[Path] = []
    for d in search_dirs:
        for f in filenames:
            out.append(d / f)
    return out


@st.cache_resource(show_spinner=False)
def _file_index() -> dict[str, Path]:
    """
    Map basename -> path for common dashboard assets.
    This allows the app to find files even if they are stored in a different
    subfolder than expected.
    """
    exts = {".png", ".jpg", ".jpeg", ".csv", ".xlsx"}
    idx: dict[str, Path] = {}
    try:
        for p in APP_DIR.rglob("*"):
            if p.is_file() and p.suffix.lower() in exts:
                # Keep first occurrence to avoid surprising swaps.
                idx.setdefault(p.name, p)
    except Exception:  # pragma: no cover
        return {}
    return idx


def find_first_existing(*filenames: str) -> Path | None:
    for p in _candidate_paths(*filenames):
        if p.exists():
            return p
    idx = _file_index()
    for f in filenames:
        hit = idx.get(f)
        if hit and hit.exists():
            return hit
    return None


def safe_image(*filenames: str, caption: str | None = None) -> None:
    p = find_first_existing(*filenames)
    if not p:
        st.warning(f"Missing image file: tried {', '.join(filenames)}")
        return
    st.image(str(p), use_container_width=True, caption=caption)


@st.cache_data(show_spinner=False)
def load_csv(filename: str) -> pd.DataFrame:
    p = find_first_existing(filename)
    if not p:
        raise FileNotFoundError(f"Could not find `{filename}` in app folder or known subfolders.")
    return pd.read_csv(p)


@st.cache_data(show_spinner=False)
def load_excel_sheet(filename: str, sheet_name: str) -> pd.DataFrame:
    p = find_first_existing(filename)
    if not p:
        raise FileNotFoundError(f"Could not find `{filename}` in app folder or known subfolders.")
    return pd.read_excel(p, sheet_name=sheet_name)


def section_title(title: str, subtitle: str | None = None) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


section_title(
    "UK Gaming Industry — Skill Demand Analysis Dashboard",
    "University of Leicester | AI for Business Intelligence | Kabilan",
)


with st.sidebar:
    st.markdown("### Navigation")
    tab = st.radio(
        "Select a section",
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
    st.markdown(
        """
<div class="small-muted">
<b>TAB 1</b>: UK headline stats + top skills.<br/>
<b>TAB 2</b>: Regional skill demand + clusters (normalised /100k).<br/>
<b>TAB 3</b>: Stage A→D gap pipeline + workshop priorities.<br/>
<b>TAB 4</b>: Experience distribution + gap skills by level.<br/>
<b>TAB 5</b>: Fair global comparison using skill share (% of jobs).<br/>
</div>
""",
        unsafe_allow_html=True,
    )


if tab == "TAB 1 — UK Overview":
    st.subheader("UK Overview")

    with st.spinner("Loading UK overview data…"):
        _df_a = load_csv("step_a_clean_output.csv")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Jobs", "1,121")
    c2.metric("Unique Skills", "352")
    c3.metric("UK Regions", "4")
    c4.metric("Date Range", "Jul–Oct 2025")

    st.markdown("### Category breakdown")
    safe_image(
        "gaming_skill_categories__2_.png",
        "gaming_skill_categories.png",
        caption="Gaming skill categories breakdown",
    )

    st.markdown("### Top 10 skills across tiers")
    top10 = pd.DataFrame(
        [
            (1, "Communication", 560, 1060, 1620, "All 3 tiers"),
            (2, "Team Management", 335, 696, 1031, "All 3 tiers"),
            (3, "Talent Acquisition", 317, 688, 1005, "All 3 tiers"),
            (4, "Cross-Functional", 168, 396, 564, "All 3 tiers"),
            (5, "Python", 134, 267, 401, "All 3 tiers"),
            (6, "Excel", 124, 302, 421, "All 3 tiers"),
            (7, "Quality-Control", 124, "—", 314, "Gaming+Trans"),
            (8, "Problem-Solving", 127, 233, 360, "All 3 tiers"),
            (9, "Unity", 122, "—", "—", "Gaming ONLY"),
            (10, "C++", 121, "—", "—", "Gaming ONLY"),
        ],
        columns=["Rank", "Skill", "Gaming Posts", "Tech Posts", "Transferable Posts", "Type"],
    )
    st.dataframe(top10, use_container_width=True, hide_index=True)

    st.markdown(
        """
<div class="callout">
<b>Insight</b><br/>
Communication leads ALL 3 tiers. Unity and C++ are gaming-exclusive skills.
</div>
""",
        unsafe_allow_html=True,
    )


elif tab == "TAB 2 — Regional Analysis":
    st.subheader("Regional Analysis")

    st.markdown("### UK regional demand heatmap")
    safe_image(
        "stage2_heatmap.png",
        "gaming_regional_analysis (3).png",
        "Gaming_UK_Skills.png",
        caption="Regional skill demand (heatmap)",
    )

    st.markdown("### Top 5 skills per region (counts + normalised /100k)")
    regions = {
        "England": [
            ("Communication", "527", "0.93/100k"),
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
    cols = st.columns(4)
    for col, (region, rows) in zip(cols, regions.items()):
        with col:
            st.markdown(f"#### {region}")
            card = pd.DataFrame(rows, columns=["Skill", "Posts", "Normalised"])
            st.dataframe(card, use_container_width=True, hide_index=True)

    st.markdown("### Normalised cluster composition")
    safe_image(
        "chart_cluster_normalised.png",
        "chart_cluster_normalised (3).png",
        caption="Normalised cluster composition",
    )

    cluster = pd.DataFrame(
        [
            ("England", 3.55, 3.55, 1.49, 1.45, 0.72, 0.71),
            ("Scotland", 2.19, 1.60, 0.93, 0.44, 0.47, 0.18),
            ("Wales", 1.06, 0.47, 0.09, 0.16, 0.22, 0.28),
            ("Northern Ireland", 1.88, 1.20, 0.58, 0.21, 0.37, 0.00),
        ],
        columns=[
            "Region",
            "Game Dev",
            "Soft Skills",
            "Project Mgmt",
            "Creative",
            "Biz Tools",
            "Cloud",
        ],
    )
    st.dataframe(cluster, use_container_width=True, hide_index=True)


elif tab == "TAB 3 — AI Gap Analysis":
    st.subheader("AI Gap Analysis")

    st.markdown(
        """
### Pipeline (Stage A → B → C → D)
- **Stage A (Clean)**: Clean and standardise job + skill signals.
- **Stage B (Cluster)**: Group skills into interpretable clusters (e.g., Game Dev, Soft Skills).
- **Stage C (Gap scoring)**: Compute regional gap scores by cluster (demand vs capability signal).
- **Stage D (Workshops)**: Convert gap + demand into prioritised workshop recommendations.
"""
    )

    st.markdown("### Gap score heatmap")
    safe_image("chart4_heatmap.png", caption="Gap score heatmap")

    heatmap_values = pd.DataFrame(
        [
            ("England", 5.07, 5.09, 5.09, 5.21, 5.26, 5.09),
            ("Scotland", 4.74, 4.25, 4.62, 4.82, 4.75, 4.82),
            ("Wales", 3.41, 3.50, 3.59, 4.18, 4.64, 4.66),
            ("Northern Ireland", 2.77, 0.00, 3.90, 4.63, 4.52, 4.69),
        ],
        columns=["Region", "Biz Tools", "Cloud", "Game Dev", "Proj Mgmt", "Soft Skills", "Creative"],
    )
    st.dataframe(heatmap_values, use_container_width=True, hide_index=True)

    st.markdown("### England distribution views")
    a, b = st.columns(2)
    with a:
        safe_image("chart3_scatter_england.png")
    with b:
        safe_image("chart1_boxplot.png")

    st.markdown("### Priority stack")
    safe_image("chart2_stacked_bar__1_.png", "chart2_stacked_bar (1).png")

    with st.spinner("Loading workshop recommendations…"):
        rec = load_csv("step_d_workshop_recommendations.csv")

    rec = rec.rename(
        columns={
            "UK_Region": "Region",
            "Priority_Rank": "Rank",
            "Skill_Cluster": "Cluster",
            "Demand_Count": "Demand",
            "Gap_Score": "Gap Score",
        }
    )

    def _priority_from_text(x: str) -> str:
        s = str(x).upper()
        if "HIGH" in s:
            return "HIGH"
        if "MEDIUM" in s:
            return "MED"
        return "STD"

    rec["Priority"] = rec.get("Workshop_Recommendation", "").map(_priority_from_text)
    rec_view = rec[["Region", "Rank", "Skill", "Cluster", "Demand", "Gap Score", "Priority"]].copy()

    st.markdown("### Filtered recommendations")
    region_opt = ["All"] + sorted(rec_view["Region"].dropna().unique().tolist())
    selected = st.selectbox("Region filter", region_opt, index=0)
    if selected != "All":
        rec_view = rec_view[rec_view["Region"] == selected]

    def _style_priority(row: pd.Series) -> list[str]:
        p = row.get("Priority", "STD")
        if p == "HIGH":
            return ["background-color: rgba(239,68,68,0.20)"] * len(row)
        if p == "MED":
            return ["background-color: rgba(249,115,22,0.18)"] * len(row)
        return ["background-color: rgba(34,197,94,0.14)"] * len(row)

    st.dataframe(
        rec_view.style.apply(_style_priority, axis=1),
        use_container_width=True,
        hide_index=True,
    )


elif tab == "TAB 4 — Experience Analysis":
    st.subheader("Experience Analysis")

    t1, t2 = st.tabs(["Overview", "Deep Analysis"])

    with t1:
        st.markdown("### Overview")
        safe_image("chart1_experience_pie__1_.png", "chart1_experience_pie (1).png")

        c1, c2 = st.columns(2)
        with c1:
            safe_image("chart2_avg_exp_by_category.png")
        with c2:
            safe_image("chart3_region_experience.png")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("No exp stated", "59.7%")
        m2.metric("Mid-level", "55.5%")
        m3.metric("Entry level", "6.0%")
        m4.metric("HR average", "8.2 yrs")

    with t2:
        st.markdown("### Deep Analysis")
        safe_image("chart_exp_heatmap.png", "chart_exp_heatmap (1).png")

        c1, c2 = st.columns(2)
        with c1:
            safe_image("chart_exp_gap_skills.png")
        with c2:
            safe_image("chart_exp_universal.png")

        st.markdown("### Gap skills by experience level")
        gap_by_exp = pd.DataFrame(
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
        st.dataframe(gap_by_exp, use_container_width=True, hide_index=True)

        st.markdown(
            """
<div class="callout">
<b>Insight</b><br/>
Communication has 9.2× more mid-level jobs than entry level. Team Management has 12.9× more.
SideFest needs a 3–5 year pathway not one-off workshops.
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("### Universal skills (appear in ALL 5 experience levels)")
        universal_csv = find_first_existing("universal_skills.csv", "chart_exp_universal_skills.csv")
        if universal_csv and universal_csv.suffix.lower() == ".csv":
            u = pd.read_csv(universal_csv)
            skills = (
                u.iloc[:, 0].dropna().astype(str).str.strip().tolist()
                if not u.empty
                else []
            )
        else:
            skills = []
        if not skills:
            st.warning(
                "Universal skills list CSV not found. If you have a CSV for the 26 universal skills, "
                "place it next to `app.py` as `universal_skills.csv` (single column: Skill)."
            )
        else:
            st.markdown("".join([f'<span class="badge">{s}</span>' for s in skills]), unsafe_allow_html=True)


elif tab == "TAB 5 — Global Comparison":
    st.subheader("Global Comparison")

    st.markdown("**Fair comparison method (no raw counts)**  ")
    st.markdown("We compare countries using **skill share** (not raw counts):")
    st.latex(
        r"\text{skill share}_{country} = \frac{\#(jobs\ mentioning\ skill\ in\ country)}{\#(all\ jobs\ in\ country)}"
    )
    st.markdown("This removes bias from countries having more job rows.")

    st.markdown("### Data source")
    st.caption(
        "This tab can use a bundled dataset (if present) or you can upload the Excel/CSV on demand."
    )

    xlsx_name = "Updated_27_02_26_-_Kabilan.xlsx"
    csv_name = "global_combined_data.csv"

    src_xlsx = find_first_existing(xlsx_name)
    src_csv = find_first_existing(csv_name)

    uploaded = st.file_uploader(
        "Upload global dataset (Excel with sheet 'Combined Data' or a CSV export)",
        type=["xlsx", "csv"],
    )

    with st.spinner("Loading global combined dataset…"):
        if uploaded is not None:
            if uploaded.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded, sheet_name="Combined Data")
        elif src_csv is not None:
            df = pd.read_csv(src_csv)
        elif src_xlsx is not None:
            df = pd.read_excel(src_xlsx, sheet_name="Combined Data")
        else:
            st.info(
                "No global dataset found in the project folder. "
                f"Either add `{xlsx_name}` (or `{csv_name}`) anywhere under this project, "
                "or upload it above to use Tab 5."
            )
            st.stop()

    # Flexible column mapping (sheet headers can vary slightly).
    cols_lower = {c.lower(): c for c in df.columns}
    def pick(*names: str) -> str | None:
        for n in names:
            if n.lower() in cols_lower:
                return cols_lower[n.lower()]
        return None

    col_company = pick("Company Category", "Company_Category", "company_category")
    col_country = pick("Country", "country", "Job Country", "job_country")
    col_skill = pick("Skill", "skill", "Skill Name", "skill_name")

    missing = [k for k, v in {"Company Category": col_company, "Country": col_country, "Skill": col_skill}.items() if v is None]
    if missing:
        st.error(
            "Your `Combined Data` sheet is missing required columns: "
            + ", ".join(missing)
            + ".\n\nExpected something like: Company Category, Country, Skill."
        )
        st.stop()

    df = df[df[col_company].astype(str).str.strip().eq("Gaming Company")].copy()
    st.caption(f"Filtered to Gaming Company rows: {len(df):,}")

    # Skill search / selection
    skill_query = st.text_input("Skill search", value="communication").strip()
    if not skill_query:
        st.stop()

    # Match skills (case-insensitive contains); fall back to exact lower match.
    skills_all = df[col_skill].dropna().astype(str)
    matches = skills_all[skills_all.str.lower().str.contains(skill_query.lower(), na=False)].unique().tolist()
    if not matches:
        exact = skills_all[skills_all.str.lower().eq(skill_query.lower())].unique().tolist()
        matches = exact

    if not matches:
        st.warning("No matching skills found in the global dataset.")
        st.stop()

    selected_skill = st.selectbox("Select matched skill", sorted(matches), index=0)

    # Compute share by country for selected skill
    base = df[[col_country, col_skill]].dropna().copy()
    base[col_country] = base[col_country].astype(str).str.strip()
    base[col_skill] = base[col_skill].astype(str).str.strip()

    totals = base.groupby(col_country, dropna=False).size().rename("Total Jobs")
    hits = base[base[col_skill].str.lower().eq(str(selected_skill).lower())].groupby(col_country).size().rename("Skill Jobs")
    share = (
        pd.concat([totals, hits], axis=1)
        .fillna({"Skill Jobs": 0})
        .assign(Share=lambda x: x["Skill Jobs"] / x["Total Jobs"])
        .sort_values("Share", ascending=False)
        .reset_index()
        .rename(columns={col_country: "Country"})
    )

    top15 = share.head(15).copy()
    uk_row = share[share["Country"].str.upper().eq("UNITED KINGDOM") | share["Country"].str.upper().eq("UK")]
    uk_country_label = uk_row["Country"].iloc[0] if not uk_row.empty else "United Kingdom"

    st.markdown("### Top 15 countries by skill share")
    if px is None:
        st.warning("Plotly is not available. Install `plotly` to view the bar chart.")
    else:
        top15["Share %"] = top15["Share"] * 100.0
        top15["Highlight"] = top15["Country"].apply(
            lambda c: "UK" if str(c).strip().lower() in {uk_country_label.strip().lower(), "united kingdom", "uk"} else "Other"
        )
        fig = px.bar(
            top15.sort_values("Share %", ascending=True),
            x="Share %",
            y="Country",
            orientation="h",
            color="Highlight",
            color_discrete_map={"UK": "#f97316", "Other": "#60a5fa"},
            title=f"Skill share for: {selected_skill}",
        )
        fig.update_layout(height=520, legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)

    # UK rank metric + insight
    share_ranked = share.copy()
    share_ranked["Rank"] = share_ranked["Share"].rank(method="min", ascending=False).astype(int)
    n_countries = int(share_ranked["Country"].nunique())
    uk_candidates = share_ranked[
        share_ranked["Country"].str.upper().isin(["UNITED KINGDOM", "UK"])
        | share_ranked["Country"].str.upper().str.contains("UNITED KINGDOM", na=False)
    ]
    if uk_candidates.empty:
        st.warning("UK row not found (country naming differs). UK rank/insight may be unavailable.")
    else:
        uk_rank = int(uk_candidates.sort_values("Rank").iloc[0]["Rank"])
        uk_share = float(uk_candidates.sort_values("Rank").iloc[0]["Share"])
        global_avg = float(share_ranked["Share"].mean())
        st.metric("UK rank", f"UK ranks #{uk_rank} out of {n_countries} countries for this skill")

        demanded_in = int((share_ranked["Skill Jobs"] > 0).sum())
        above = "above" if uk_share >= global_avg else "below"
        st.info(
            f"{selected_skill} is demanded in {demanded_in} countries. "
            f"UK skill share is {uk_share*100:.2f}%. Global average is {global_avg*100:.2f}%. "
            f"UK is {above} the global average."
        )

    st.markdown("### UK skill ranking vs global ranking (top 20 UK by share)")
    # UK top 20 skills by share
    uk_mask = base[col_country].str.upper().isin(["UNITED KINGDOM", "UK"]) | base[col_country].str.upper().str.contains(
        "UNITED KINGDOM", na=False
    )
    uk_base = base[uk_mask].copy()
    if uk_base.empty:
        st.warning("Cannot compute UK top-20 shares (UK country rows not found).")
        st.stop()

    uk_tot = len(uk_base)
    uk_skill_counts = uk_base.groupby(col_skill).size().rename("UK Skill Jobs").sort_values(ascending=False)
    uk_top20 = uk_skill_counts.head(20).reset_index().rename(columns={col_skill: "Skill"})
    uk_top20["UK Share %"] = (uk_top20["UK Skill Jobs"] / uk_tot) * 100.0
    uk_top20["UK Rank"] = uk_top20["UK Share %"].rank(method="min", ascending=False).astype(int)

    # Global ranks for those same skills
    global_tot_by_country = totals  # from earlier (all countries)
    global_tot = len(base)
    global_skill_counts = base.groupby(col_skill).size().rename("Global Skill Jobs")
    global_share_all = (global_skill_counts / global_tot * 100.0).rename("Global Share %").reset_index().rename(columns={col_skill: "Skill"})
    global_share_all["Global Rank"] = global_share_all["Global Share %"].rank(method="min", ascending=False).astype(int)

    comp = uk_top20.merge(global_share_all, on="Skill", how="left")
    comp["Trend"] = comp.apply(
        lambda r: "↑" if (pd.notna(r["Global Rank"]) and int(r["UK Rank"]) < int(r["Global Rank"])) else "↓",
        axis=1,
    )
    comp_view = comp[["Skill", "UK Share %", "UK Rank", "Global Share %", "Global Rank", "Trend"]].copy()
    st.dataframe(comp_view, use_container_width=True, hide_index=True)

    st.markdown(
        """
<div class="callout">
<b>What this means for SideFest</b><br/>
This comparison highlights where the UK’s demand is disproportionately high (or low) versus the global baseline.
SideFest can prioritise interventions where the UK’s rank suggests a relative shortage or strategic capability gap.
</div>
""",
        unsafe_allow_html=True,
    )

