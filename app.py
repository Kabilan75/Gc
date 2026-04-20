"""UK Gaming Industry — Skill Intelligence Dashboard (Streamlit)."""
from __future__ import annotations
import hashlib
import io
import re
import shutil
import warnings
from pathlib import Path

import numpy as np
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

# ── Theme CSS (main + sidebar nav pills) ─────────────────────────────────────
st.markdown("""
<style>
/* Sidebar above main so wide main pane never paints over sidebar text */
section[data-testid="stSidebar"] {
  background-color: #0C1422;
  position: relative;
  z-index: 100;
  min-width: 17rem;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stRadio div { color: #CBD5E1 !important; }
/* Nav pills (sidebar radio only) */
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] {
  gap: 8px !important;
  flex-direction: column !important;
  align-items: stretch !important;
}
section[data-testid="stSidebar"] .stRadio label {
  border: 1px solid #1E293B !important;
  border-radius: 10px !important;
  padding: 0.6rem 0.85rem !important;
  margin: 0 !important;
  background: rgba(17, 29, 46, 0.9) !important;
  cursor: pointer !important;
  transition: border-color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
}
section[data-testid="stSidebar"] .stRadio label:hover {
  border-color: #334155 !important;
  background: rgba(30, 41, 59, 0.95) !important;
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
  border-color: #00E5CC !important;
  background: rgba(0, 229, 204, 0.1) !important;
  box-shadow: 0 0 0 1px rgba(0, 229, 204, 0.35);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) p,
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
  color: #F0F4F8 !important;
}
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
h1, h2, h3, h4 { color: #F0F4F8 !important; }
p, li { color: #CBD5E1; }
/* Compact metrics + expanders (main pane only; sidebar unchanged) */
section[data-testid="stMain"] div[data-testid="metric-container"] {
  padding: 0.45rem 0.65rem !important;
  min-height: 0 !important;
}
section[data-testid="stMain"] div[data-testid="metric-container"] [data-testid="stMetricLabel"] p {
  font-size: 0.72rem !important;
  line-height: 1.2 !important;
  margin-bottom: 0.1rem !important;
}
section[data-testid="stMain"] div[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-size: 1.35rem !important;
  line-height: 1.15 !important;
}
section[data-testid="stMain"] div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
  font-size: 0.78rem !important;
  line-height: 1.2 !important;
  margin-top: 0.15rem !important;
}
section[data-testid="stMain"] [data-testid="stExpander"] details > summary {
  padding-top: 0.4rem !important;
  padding-bottom: 0.4rem !important;
  min-height: 0 !important;
}
section[data-testid="stMain"] [data-testid="stExpander"] [data-testid="stVerticalBlockBorderWrapper"] {
  padding-top: 0.25rem !important;
  padding-bottom: 0.35rem !important;
}
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

# Display totals for UK Overview (verified counts; Step A long-form rows undercount unique ads)
UK_OVERVIEW_TOTAL_JOB_ADS = 1121
UK_OVERVIEW_UNIQUE_SKILLS = 352

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

# ── CV Evaluator — role buckets + aliases (skills gated by Step A vocabulary) ──
CV_JOB_CATS: dict[str, list[str]] = {
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
CV_SKILL_ALIASES: list[tuple[str, str]] = [
    ("unreal engine", "unreal"),
    ("unrealengine", "unreal"),
    ("ue5", "unreal"),
    ("ue4", "unreal"),
    ("c plus plus", "cpp"),
    ("cplusplus", "cpp"),
    ("c sharp", "c#"),
    ("csharp", "c#"),
    ("ms office", "ms-office"),
    ("machine learning", "machine-learning"),
    ("node.js", "node"),
    ("nodejs", "node"),
    ("ci/cd", "ci-cd"),
    ("ci cd", "ci-cd"),
    ("user experience", "user-experience-ux"),
    ("ux design", "user-experience-ux"),
]
_CV_REGEX_SPECIAL: dict[str, str] = {
    "cpp": r"c\s*\+\s*\+|(?<![a-z0-9])cplusplus(?![a-z0-9])",
    "c#": r"c\s*#|(?<![a-z0-9])c\s*sharp(?![a-z0-9])",
    "ci-cd": r"ci\s*/\s*cd|(?<![a-z0-9])ci[-\s]+cd(?![a-z0-9])",
}
CV_FALLBACK_VOCAB: list[str] = sorted(
    {
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
    }
)


def _cv_vocab_from_step_a(df: pd.DataFrame) -> list[str]:
    if df is None or df.empty or "Skills" not in df.columns:
        return list(CV_FALLBACK_VOCAB)
    ser = df["Skills"].dropna().astype(str).str.strip()
    ser = ser[ser.str.len() > 0]
    if ser.empty:
        return list(CV_FALLBACK_VOCAB)
    return sorted(ser.str.lower().unique())


def _cv_slug_regex(slug: str) -> str:
    parts = slug.split("-")
    if len(parts) == 1:
        return r"(?<![a-z0-9+])" + re.escape(slug) + r"(?![a-z0-9+])"
    return r"(?<![a-z0-9+])" + r"[-\s]+".join(re.escape(p) for p in parts) + r"(?![a-z0-9+])"


def _cv_phrase_regex(phrase: str) -> str:
    phrase = phrase.strip().lower()
    parts = phrase.split()
    if len(parts) == 1:
        return r"(?<![a-z0-9+])" + re.escape(parts[0]) + r"(?![a-z0-9+])"
    return r"(?<![a-z0-9+])" + r"[-\s]+".join(re.escape(p) for p in parts) + r"(?![a-z0-9+])"


def _cv_detect_skills(text: str, vocab: list[str]) -> list[str]:
    if not text or not vocab:
        return []
    t = text.lower()
    vocab_set = set(vocab)
    found: set[str] = set()
    for phrase, slug in sorted(CV_SKILL_ALIASES, key=lambda x: -len(x[0])):
        if slug not in vocab_set or slug in found:
            continue
        if re.search(_cv_phrase_regex(phrase), t):
            found.add(slug)
    rest = sorted(vocab_set - found, key=lambda x: (-len(x), x))
    for slug in rest:
        if slug in _CV_REGEX_SPECIAL:
            if re.search(_CV_REGEX_SPECIAL[slug], t, re.IGNORECASE):
                found.add(slug)
            continue
        if re.search(_cv_slug_regex(slug), t, re.IGNORECASE):
            found.add(slug)
    return sorted(found)


def _cv_top_priority_skills(df: pd.DataFrame, n: int = 10) -> list[str]:
    if df is None or df.empty or "Skills" not in df.columns:
        return list(CV_FALLBACK_VOCAB[: min(n, len(CV_FALLBACK_VOCAB))])
    vc = df["Skills"].dropna().astype(str).str.strip().str.lower().value_counts()
    if vc.empty:
        return list(CV_FALLBACK_VOCAB[: min(n, len(CV_FALLBACK_VOCAB))])
    return list(vc.head(n).index)


def _cv_demand_weighted_pct(df: pd.DataFrame, found: set[str]) -> float:
    if df is None or df.empty or "Skills" not in df.columns or not found:
        return 0.0
    ser = df["Skills"].dropna().astype(str).str.strip().str.lower()
    total = int(len(ser))
    if total == 0:
        return 0.0
    hit = int(ser.isin(found).sum())
    return round(100.0 * hit / total, 1)


def _cv_listing_overlap(df: pd.DataFrame, found: set[str]) -> tuple[float, int, int]:
    if df is None or df.empty or "Skills" not in df.columns or not found:
        return 0.0, 0, 0
    cols = [c for c in df.columns if c != "Skills"]
    if not cols:
        return 0.0, 0, 0
    dedup_keys = df[cols].fillna("").astype(str).apply(lambda r: "||".join(r.values), axis=1)
    tmp = df.assign(_k=dedup_keys)
    hits = 0
    groups = 0
    for _, g in tmp.groupby("_k", sort=False):
        groups += 1
        sk = set(str(x).strip().lower() for x in g["Skills"].dropna().astype(str))
        if sk & found:
            hits += 1
    if groups == 0:
        return 0.0, 0, 0
    return round(100.0 * hits / groups, 1), hits, groups


def _cv_category_scores(found: set[str], vocab_set: set[str]) -> list[tuple[str, float, int, int]]:
    scores: list[tuple[str, float, int, int]] = []
    for cat, skills in CV_JOB_CATS.items():
        rel = [s for s in skills if s in vocab_set]
        if not rel:
            continue
        matched = [s for s in rel if s in found]
        score = round(len(matched) / len(rel) * 100, 1)
        scores.append((cat, score, len(matched), len(rel)))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def match_jobs_to_cv(
    df_a,
    detected_skills,
    df_global=None,
    top_n=20,
):
    if df_a is None or df_a.empty:
        return pd.DataFrame()
    if "Skills" not in df_a.columns:
        return pd.DataFrame()
    if not detected_skills:
        return pd.DataFrame()

    skills_lower = [s.lower() for s in detected_skills]

    matched = df_a[df_a["Skills"].astype(str).str.lower().isin(skills_lower)].copy()

    if matched.empty:
        return pd.DataFrame()

    id_cols = [c for c in df_a.columns if c not in ("Skills", "_job_id")]

    # Count UNIQUE matched skills per job listing (not repeated rows/mentions).
    matched["_skill_norm"] = matched["Skills"].astype(str).str.strip().str.lower()
    job_groups = (
        matched.groupby(id_cols, dropna=False)["_skill_norm"]
        .nunique()
        .reset_index(name="Skills_Matched")
    )

    if "Activated Date" in job_groups.columns:
        job_groups["Activated Date"] = pd.to_datetime(
            job_groups["Activated Date"],
            errors="coerce",
            dayfirst=True,
        )
        job_groups = job_groups.sort_values(["Skills_Matched", "Activated Date"], ascending=[False, False])
    else:
        job_groups = job_groups.sort_values("Skills_Matched", ascending=False)

    # Try to merge job title and apply link from df_global workbook
    if df_global is not None and not df_global.empty:

        # Find title column
        title_col = None
        for c in df_global.columns:
            if c.lower() in (
                "title",
                "job title",
                "jobtitle",
                "role",
                "position",
                "job role",
                "job_title",
                "job name",
            ):
                title_col = c
                break

        # Find link column
        link_col = None
        for c in df_global.columns:
            if c.lower() in (
                "job link",
                "link",
                "url",
                "apply link",
                "job url",
                "application url",
                "apply url",
                "job_link",
                "applylink",
                "joblink",
                "application link",
            ):
                link_col = c
                break

        # Find date column in global for joining
        date_col = None
        for c in df_global.columns:
            if c.lower() in (
                "activated date",
                "date",
                "posted date",
                "activation date",
                "activateddate",
            ):
                date_col = c
                break

        # Build a lookup from df_global
        if title_col or link_col:
            keep_cols = ["Country", "State"]
            if date_col:
                keep_cols.append(date_col)
            if title_col:
                keep_cols.append(title_col)
            if link_col:
                keep_cols.append(link_col)

            # Only keep columns that exist
            keep_cols = [c for c in keep_cols if c in df_global.columns]

            global_lookup = df_global[keep_cols].copy()
            global_lookup = global_lookup.drop_duplicates()

            # Rename columns to match job_groups
            rename_map = {}
            if title_col:
                rename_map[title_col] = "Job Role"
            if link_col:
                rename_map[link_col] = "Apply Link"
            if date_col and date_col != "Activated Date":
                rename_map[date_col] = "Activated Date"

            global_lookup = global_lookup.rename(columns=rename_map)

            if "Activated Date" in global_lookup.columns:
                global_lookup["Activated Date"] = pd.to_datetime(
                    global_lookup["Activated Date"],
                    errors="coerce",
                    dayfirst=True,
                )

            # Merge on common columns
            merge_cols = [
                c
                for c in ["Country", "State", "Activated Date"]
                if c in job_groups.columns and c in global_lookup.columns
            ]

            if merge_cols:
                job_groups = job_groups.merge(global_lookup, on=merge_cols, how="left")

    return job_groups.head(top_n)


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
    """Mean Gap_Score per UK Region × Cluster_Name from Step C (live CSV)."""
    need = {"UK Region", "Cluster_Name", "Gap_Score"}
    if df_c is None or df_c.empty or not need.issubset(df_c.columns):
        return [], [], []
    df = df_c.copy()
    df["UK Region"] = df["UK Region"].astype(str).str.strip()
    df["Cluster_Name"] = df["Cluster_Name"].astype(str).str.strip()
    df["Gap_Score"] = pd.to_numeric(df["Gap_Score"], errors="coerce")
    df = df.dropna(subset=["Gap_Score"])
    if df.empty:
        return [], [], []
    g = df.groupby(["UK Region", "Cluster_Name"], as_index=False)["Gap_Score"].mean()
    pivot = g.pivot(index="UK Region", columns="Cluster_Name", values="Gap_Score")
    cluster_order = [
        "Game Development & Programming",
        "Soft Skills & Business Development",
        "Project & Development Management",
        "Soft Skills & Creative Production",
        "Business Tools & Productivity",
        "Cloud, Infrastructure & DevOps",
    ]
    pivot = pivot.reindex(columns=cluster_order)
    row_order = ["England", "Scotland", "Wales", "Northern Ireland"]
    rows = [r for r in row_order if r in pivot.index]
    if not rows:
        return [], [], []
    pivot = pivot.reindex(index=rows)
    z = pivot.fillna(0).values.tolist()
    y = [_reg_display(r) for r in rows]
    x = [_short_cluster(str(c)) for c in cluster_order]
    return z, x, y


def _is_uk_country_mask(country_series: pd.Series) -> pd.Series:
    s = country_series.astype(str).str.strip().str.lower()
    return s.isin({"united kingdom", "uk", "u.k.", "gb", "great britain"})


# ── Global tab (improved: dedupe + binary skill shares) ─────────────────────
SKILL_NORM_MAP = {
    "cpp": "C++",
    "c++": "C++",
    "c plus plus": "C++",
    "c#": "C#",
    "csharp": "C#",
    "c sharp": "C#",
    "ms-office": "MS Office",
    "microsoft office": "MS Office",
    "microsoft-office": "MS Office",
    "real-time-vfx": "Real-Time VFX",
    "realtime vfx": "Real-Time VFX",
    "agile-development": "Agile Development",
    "agile development": "Agile Development",
    "agile": "Agile Development",
    "talent-acquisition": "Talent Acquisition",
    "team-management": "Team Management",
    "cross-functional": "Cross-Functional",
    "quality-control": "Quality Control",
    "budget-management": "Budget Management",
    "problem-solving": "Problem Solving",
    "data-analytics": "Data Analytics",
    "machine-learning": "Machine Learning",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "user-experience-ux": "UX / User Experience",
    "ux": "UX / User Experience",
    "ci-cd": "CI/CD",
    "cicd": "CI/CD",
    "ci/cd": "CI/CD",
    "timeline-management": "Timeline Management",
    "back-end": "Back-End Dev",
    "backend": "Back-End Dev",
    "lighting-shading": "Lighting & Shading",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "sql": "SQL",
    "nosql": "NoSQL",
    "unity": "Unity",
    "unreal": "Unreal Engine",
    "unreal engine": "Unreal Engine",
    "communication": "Communication",
    "storytelling": "Storytelling",
    "photoshop": "Photoshop",
    "maya": "Maya",
    "blender": "Blender",
    "figma": "Figma",
    "tableau": "Tableau",
    "power-bi": "Power BI",
    "power bi": "Power BI",
    "excel": "Excel",
    "git": "Git",
    "github": "GitHub",
    "jira": "Jira",
    "confluence": "Confluence",
    "linux": "Linux",
    "salesforce": "Salesforce",
}


def normalise_skill(raw: object) -> str:
    s = str(raw).strip()
    if not s:
        return ""
    k = s.lower().strip()
    # Treat common separators consistently for lookup.
    k = re.sub(r"\s*/\s*", "-", k)
    k_space = k.replace("-", " ").strip()
    if k_space in SKILL_NORM_MAP:
        return SKILL_NORM_MAP[k_space]
    if k in SKILL_NORM_MAP:
        return SKILL_NORM_MAP[k]
    if k_space in {"ci cd"} or k in {"ci-cd", "ci/cd"}:
        return "CI/CD"
    if k in {"c++", "cplusplus", "c plus plus"} or k_space in {"c++"}:
        return "C++"
    return s.replace("-", " ").title()


def normalise_country(raw: object) -> str:
    city_to_country = {
        # UK-only cities (avoid ambiguous cities like Cambridge/Oxford/Bristol/Newcastle)
        "guildford": "United Kingdom",
        "leicester": "United Kingdom",
        "dundee": "United Kingdom",
        "leamington spa": "United Kingdom",
        "royal leamington spa": "United Kingdom",
        "newcastle upon tyne": "United Kingdom",
        "glasgow": "United Kingdom",
        "edinburgh": "United Kingdom",
        "cardiff": "United Kingdom",
        "belfast": "United Kingdom",
        # UK country name variations
        "uk": "United Kingdom",
        "u.k.": "United Kingdom",
        "great britain": "United Kingdom",
        "britain": "United Kingdom",
        "england": "United Kingdom",
        "scotland": "United Kingdom",
        "wales": "United Kingdom",
        "northern ireland": "United Kingdom",
        "united kingdom (uk)": "United Kingdom",
        # US cities — unambiguous
        "new york": "United States",
        "san francisco": "United States",
        "seattle": "United States",
        "los angeles": "United States",
        "austin": "United States",
        "chicago": "United States",
        "boston": "United States",
        "el segundo": "United States",
        "santa monica": "United States",
        "san mateo": "United States",
        "salt lake city": "United States",
        "bellevue": "United States",
        "redmond": "United States",
        "irvine": "United States",
        "usa": "United States",
        "us": "United States",
        # India cities — unambiguous
        "bengaluru": "India",
        "bangalore": "India",
        "mumbai": "India",
        "pune": "India",
        "hyderabad": "India",
        "chennai": "India",
        "new delhi": "India",
        "noida": "India",
        "gurugram": "India",
        "kolkata": "India",
        # Canada
        "vancouver": "Canada",
        "toronto": "Canada",
        "montreal": "Canada",
        "calgary": "Canada",
        "edmonton": "Canada",
        "winnipeg": "Canada",
        # Germany
        "berlin": "Germany",
        "munich": "Germany",
        "hamburg": "Germany",
        "frankfurt am main": "Germany",
        "cologne": "Germany",
        "dusseldorf": "Germany",
        # Poland
        "warsaw": "Poland",
        "krakow": "Poland",
        "wroclaw": "Poland",
        "gdansk": "Poland",
        # Australia
        "sydney": "Australia",
        "melbourne": "Australia",
        "brisbane": "Australia",
        "perth": "Australia",
        # France
        "paris": "France",
        "lyon": "France",
        "montpellier": "France",
        # Japan
        "tokyo": "Japan",
        "osaka": "Japan",
        # Sweden
        "stockholm": "Sweden",
        "gothenburg": "Sweden",
        "malmo": "Sweden",
        # Ukraine
        "kyiv": "Ukraine",
        "kiev": "Ukraine",
        "kharkiv": "Ukraine",
        "lviv": "Ukraine",
        # Netherlands
        "amsterdam": "Netherlands",
        "rotterdam": "Netherlands",
        # Spain
        "madrid": "Spain",
        "barcelona": "Spain",
        # South Korea
        "seoul": "South Korea",
        "busan": "South Korea",
        # Other unambiguous
        "singapore": "Singapore",
        "dubai": "United Arab Emirates",
        "tel aviv": "Israel",
        "tel aviv-yafo": "Israel",
        "moscow": "Russia",
        "istanbul": "Turkey",
        "prague": "Czech Republic",
        "budapest": "Hungary",
        "bucharest": "Romania",
        "helsinki": "Finland",
        "oslo": "Norway",
        "copenhagen": "Denmark",
        "zurich": "Switzerland",
        "vienna": "Austria",
        "lisbon": "Portugal",
        "dublin": "Ireland",
        "sao paulo": "Brazil",
        "mexico city": "Mexico",
        "buenos aires": "Argentina",
        "kuala lumpur": "Malaysia",
        "bangkok": "Thailand",
        "jakarta": "Indonesia",
    }
    s = str(raw).strip()
    if not s:
        return ""
    k = re.sub(r"\s+", " ", s.lower().strip())
    if k in city_to_country:
        return city_to_country[k]
    return s.title()


def make_job_id(row: pd.Series) -> str:
    for id_col in ("Job_ID", "job_id", "ID", "id", "URL", "url"):
        if id_col in row.index and pd.notna(row[id_col]):
            v = str(row[id_col]).strip()
            if v and v.lower() not in {"nan", "none", "null"}:
                return v
    parts: list[str] = []
    # Preferred fingerprint for this workbook shape.
    fp_cols = ["Company Category", "Country", "State", "Activated Date"]
    if all(c in row.index for c in fp_cols):
        for c in fp_cols:
            parts.append(str(row.get(c, "")).strip().lower())
    else:
        # Fallback: hash all columns except `Skills` / derived helpers.
        for col in row.index:
            if col in {"Skills", "_skills_list"}:
                continue
            parts.append(str(row[col]).strip().lower())
        if not parts:
            parts = [str(v).strip().lower() for v in row.values]
    fp = "|".join(parts)
    return hashlib.md5(fp.encode("utf-8", errors="replace")).hexdigest()


def deduplicate_jobs(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    out["_job_id"] = out.apply(make_job_id, axis=1)
    out = out.drop_duplicates(subset=["_job_id"], keep="first")
    return out.reset_index(drop=True)


def extract_skills(raw_skills: object) -> list[str]:
    if not raw_skills or pd.isna(raw_skills):
        return []
    s = str(raw_skills).strip()
    if s.lower() in ("nan", "none", ""):
        return []
    # Protect slash-containing skills before splitting.
    s = re.sub(r"(?i)\bci\s*/\s*cd\b", "CICD_PROTECTED", s)
    # Split on comma and semicolon only (not slash).
    tokens = re.split(r"[,;]+", s)
    result: list[str] = []
    for tok in tokens:
        tok = tok.strip()
        tok = tok.replace("CICD_PROTECTED", "ci-cd")
        if not tok or tok.lower() in ("nan", "none", "", "game-texts", "null"):
            continue
        normalised = normalise_skill(tok)
        if normalised and len(normalised) > 1:
            result.append(normalised)
    return result


def build_binary_skill_matrix(
    df_jobs: pd.DataFrame,
    *,
    top_n_skills: int = 50,
) -> tuple[pd.DataFrame, list[str]]:
    if df_jobs is None or df_jobs.empty or "Skills" not in df_jobs.columns:
        return pd.DataFrame(), []
    df = df_jobs.copy()
    if "Country" not in df.columns:
        return pd.DataFrame(), []
    df["Skills"] = df["Skills"].fillna("").astype(str)
    df["_skills_list"] = df["Skills"].apply(extract_skills)

    skill_counts: dict[str, int] = {}
    for skills_list in df["_skills_list"]:
        for sk in set(skills_list):
            skill_counts[sk] = skill_counts.get(sk, 0) + 1
    if not skill_counts:
        return pd.DataFrame(), []
    top_skills = sorted(skill_counts, key=lambda k: -skill_counts[k])[:top_n_skills]

    # Faster build than per-row dict construction.
    binary_df = pd.DataFrame(index=range(len(df)))
    binary_df["Country"] = df["Country"].astype(str).str.strip().replace({"": "Unknown"}).values
    for sk in top_skills:
        binary_df[sk] = df["_skills_list"].apply(lambda skills, s=sk: 1 if s in set(skills) else 0).values
    return binary_df, top_skills


def compute_skill_shares(binary_df: pd.DataFrame, top_skills: list[str]) -> pd.DataFrame:
    if binary_df is None or binary_df.empty or not top_skills or "Country" not in binary_df.columns:
        return pd.DataFrame()
    out: dict[str, dict[str, float]] = {}
    for country, grp in binary_df.groupby("Country", sort=False):
        n = int(len(grp))
        shares: dict[str, float] = {}
        for sk in top_skills:
            shares[sk] = float(grp[sk].sum()) / n * 100.0 if sk in grp.columns else 0.0
        out[str(country)] = shares
    return pd.DataFrame(out).T if out else pd.DataFrame()


def cosine_similarity_to_uk(share_df: pd.DataFrame, *, top_n: int = 12) -> list[tuple[str, float]]:
    if share_df is None or share_df.empty or "United Kingdom" not in share_df.index:
        return []
    uk = share_df.loc["United Kingdom"].to_numpy(dtype=float)
    uk_norm = float(np.linalg.norm(uk))
    if uk_norm < 1e-6:
        return []
    eps = 1e-9
    sims: list[tuple[str, float]] = []
    for c in share_df.index.astype(str):
        if c == "United Kingdom":
            continue
        v = share_df.loc[c].to_numpy(dtype=float)
        v_norm = float(np.linalg.norm(v))
        sim = float(np.dot(uk, v) / (uk_norm * v_norm + eps))
        sim = float(np.clip(sim, -1.0, 1.0))
        sims.append((c, round(sim, 4)))
    sims.sort(key=lambda x: -x[1])
    return sims[:top_n]


def compute_uk_vs_world(
    share_df: pd.DataFrame,
    all_job_counts: pd.Series,
    *,
    top_n: int = 7,
) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    if share_df is None or share_df.empty or "United Kingdom" not in share_df.index:
        return [], []
    uk = share_df.loc["United Kingdom"]
    weights = pd.Series([float(all_job_counts.get(c, 1)) for c in share_df.index], index=share_df.index)
    world_avg = share_df.multiply(weights, axis=0).sum() / float(weights.sum() if float(weights.sum()) else 1.0)
    diff = uk - world_avg
    ahead_raw = diff[diff > 0.05].sort_values(ascending=False)
    behind_raw = diff[diff < -0.05].sort_values(ascending=True)
    ahead = [(str(sk), round(float(v), 2)) for sk, v in ahead_raw.head(top_n).items()]
    behind = [(str(sk), round(float(abs(v)), 2)) for sk, v in behind_raw.head(top_n).items()]
    return ahead, behind


def build_rankings_table(
    share_df: pd.DataFrame,
    all_job_counts: pd.Series,
    *,
    n_show: int = 12,
) -> pd.DataFrame:
    if share_df is None or share_df.empty or "United Kingdom" not in share_df.index:
        return pd.DataFrame()
    uk_shares = share_df.loc["United Kingdom"].sort_values(ascending=False)
    weights = pd.Series([float(all_job_counts.get(c, 1)) for c in share_df.index], index=share_df.index)
    world_avg = share_df.multiply(weights, axis=0).sum() / float(weights.sum() if float(weights.sum()) else 1.0)
    uk_rank = uk_shares.rank(ascending=False, method="min")
    world_rank = world_avg.rank(ascending=False, method="min")
    rows: list[list[object]] = []
    for sk in uk_shares.head(n_show).index:
        uk_pct = round(float(uk_shares[sk]), 2)
        w_pct = round(float(world_avg.get(sk, 0.0)), 2)
        uk_r = int(uk_rank[sk])
        w_r = int(world_rank.get(sk, 0))
        diff = uk_pct - w_pct
        trend = "↑ Ahead" if diff > 0.1 else "↓ Behind" if diff < -0.1 else "≈ Parity"
        rows.append([str(sk), uk_pct, uk_r, w_pct, w_r, trend])
    return pd.DataFrame(rows, columns=["Skill", "UK Share %", "UK Rank", "Global Avg %", "Global Rank", "Trend"])


def prepare_global_data(df_global: pd.DataFrame | None) -> pd.DataFrame:
    """Prepare Global workbook data.

    Each row is treated as one unique job listing (no collapsing / no deduplication).
    """
    if df_global is None or df_global.empty:
        return pd.DataFrame()

    base = df_global.copy()

    # Filter gaming companies only
    if "Company Category" in base.columns:
        base = base[base["Company Category"].astype(str).str.strip() == "Gaming Company"].copy()

    # Normalise country names
    if "Country" in base.columns:
        base["Country"] = base["Country"].apply(normalise_country)
        base = base[base["Country"].astype(str).str.strip().str.len() > 0].copy()

    # Each row = one job. No collapsing. No deduplication.
    return base.reset_index(drop=True)


def render_global_tab(df_global: pd.DataFrame | None, *, source_name: str | None = None) -> None:
    st.markdown("#### Global Comparison · `UK vs world`")
    st.caption("Unique job listings · binary skill presence (% of jobs mentioning skill)")
    st.markdown("---")

    STATIC_COUNTRIES = [
        ("United States", 5604),
        ("India", 2374),
        ("Canada", 1914),
        ("United Kingdom", 1634),
        ("China", 998),
        ("Poland", 867),
        ("Germany", 575),
        ("Japan", 535),
        ("Australia", 447),
        ("France", 442),
    ]
    STATIC_AHEAD = [
        ("Talent Acquisition", 18.73),
        ("Storytelling", 8.41),
        ("Team Management", 8.22),
        ("Unreal", 7.41),
        ("Maya", 6.57),
        ("C++", 6.35),
        ("Real-Time VFX", 4.61),
    ]
    STATIC_BEHIND = [
        ("CI/CD", 8.25),
        ("Python", 6.86),
        ("SQL", 5.68),
        ("Docker", 5.10),
        ("Kubernetes", 4.43),
        ("Linux", 4.41),
        ("AWS", 4.41),
    ]
    STATIC_RANKINGS = pd.DataFrame(
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
    STATIC_SIMILAR = [
        ("France", 0.96),
        ("Japan", 0.95),
        ("United States", 0.94),
        ("Sweden", 0.93),
        ("Brazil", 0.93),
        ("Spain", 0.93),
        ("UAE", 0.92),
        ("South Korea", 0.92),
        ("Netherlands", 0.92),
    ]

    use_live = False
    share_df = pd.DataFrame()
    top_skills: list[str] = []
    all_job_counts = pd.Series(dtype=int)

    top_countries = None
    uk_rank = None
    n_uk_jobs = 0
    n_total_countries = 0
    n_countries_analysed = 0

    binary_df = pd.DataFrame()
    if df_global is not None and not df_global.empty:
        if "Country" not in df_global.columns:
            st.error("Workbook loaded but missing required column `Country`.")
        elif "Skills" not in df_global.columns:
            st.error("Workbook loaded but missing required column `Skills`.")
        else:
            try:
                # STEP 1: load + filter gaming rows; each row is one job listing.
                base = prepare_global_data(df_global)

                if base is not None and not base.empty and "Country" in base.columns:
                    all_job_counts = base["Country"].astype(str).str.strip().value_counts()
                    n_total_countries = int(all_job_counts.shape[0])
                    n_uk_jobs = int(all_job_counts.get("United Kingdom", 0))

                    # STEP 4: UK rank among ALL countries by job count.
                    sorted_counts = all_job_counts.sort_values(ascending=False)
                    if "United Kingdom" in sorted_counts.index:
                        uk_rank = int(sorted_counts.index.tolist().index("United Kingdom") + 1)

                    # STEP 5: Top countries chart uses ALL countries.
                    top_countries = sorted_counts.reset_index()
                    top_countries.columns = ["Country", "Jobs"]

                    # STEP 6: 50-job threshold ONLY for skill analysis.
                    n_countries_analysed = int((all_job_counts >= 50).sum())
                    analysed_countries = set(all_job_counts[all_job_counts >= 50].index.astype(str))
                    base_analysed = base[base["Country"].astype(str).str.strip().isin(analysed_countries)].copy()

                    binary_df, top_skills = build_binary_skill_matrix(base_analysed, top_n_skills=50)
                    share_df = compute_skill_shares(binary_df, top_skills)

                    if not share_df.empty and "United Kingdom" in share_df.index:
                        use_live = True
            except Exception as ex:
                st.error(f"Error processing global workbook: {str(ex)[:220]}")

    if use_live:
        st.success(f"📡 **Live Data** — `{source_name}` · one row per job listing · binary skill shares.")
    else:
        st.warning(
            "📋 **Reference Data** — Load `Combined_Data_cleaned.xlsx` or `Updated_27_02_26_-_Kabilan.xlsx` "
            "(sheet: `Combined Data`) to enable live global comparisons. "
            "Showing 81 countries in reference data. Live mode shows countries with ≥50 jobs "
            "for skill analysis but all countries for ranking. "
            "Note: static % values use raw token counts — live values use binary presence per job so numbers will differ."
        )

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    if use_live:
        c1.metric("UK Global Rank", f"#{uk_rank}" if uk_rank else "—", f"out of {n_total_countries} total countries")
        c2.metric("UK Gaming Jobs", f"{n_uk_jobs:,}", "unique job listings")
        c3.metric("Countries for analysis", f"{n_countries_analysed}", f"{n_total_countries} total countries found")
        c4.metric("Skills tracked", "50", "top skills vocabulary")
    else:
        c1.metric("UK Global Rank", "#4", "By gaming listings")
        c2.metric("Communication", "80/81", "Countries demand it")
        c3.metric("UK Comm. Share", "52.12%", "Ranks #1 globally")
        c4.metric("Most Similar", "France", "0.96 cosine similarity")

    st.subheader("Top countries by gaming job listings")
    if use_live and top_countries is not None:
        df_top = top_countries.head(15).copy()
    else:
        df_top = pd.DataFrame(STATIC_COUNTRIES, columns=["Country", "Jobs"])
    df_top["Type"] = df_top["Country"].astype(str).map(
        lambda x: "United Kingdom" if x == "United Kingdom" else "Other"
    )
    df_top = df_top.sort_values("Jobs", ascending=False).reset_index(drop=True)
    df_top["Rank"] = df_top.index + 1
    df_top["RankLabel"] = df_top["Rank"].astype(str) + ". " + df_top["Country"].astype(str)

    fig_ct = px.bar(
        df_top,
        x="RankLabel",
        y="Jobs",
        title="Top 15 Countries — Unique Gaming Job Listings (Ranked)",
        color="Type",
        color_discrete_map={
            "United Kingdom": "#00E5CC",
            "Other": "#1E293B",
        },
        text="Jobs",
    )
    fig_ct.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        textfont=dict(size=11),
    )
    fig_ct.update_layout(
        showlegend=False,
        xaxis_title="Rank · Country",
        yaxis_title="Number of Job Listings",
        xaxis=dict(
            categoryorder="array",
            categoryarray=df_top["RankLabel"].tolist(),
        ),
    )
    _uk_rank = int(uk_rank) if (use_live and uk_rank) else int(
        df_top.loc[df_top["Country"] == "United Kingdom", "Rank"].iloc[0]
    ) if "United Kingdom" in df_top["Country"].values else 4
    fig_ct.add_annotation(
        text=f"🇬🇧 UK = #{_uk_rank} globally",
        xref="paper",
        yref="paper",
        x=0.98,
        y=0.15,
        showarrow=False,
        font=dict(size=12, color="#00E5CC"),
        bgcolor="#0C1422",
        bordercolor="#00E5CC",
        borderwidth=1,
    )
    show(fig_ct, 500)

    if use_live and not share_df.empty:
        st.subheader("Skill Explorer — UK vs world")
        st.caption("Binary presence: % of unique jobs in each country that mention the skill")
        skills_available = [str(s) for s in share_df.columns.tolist()]
        default_skill = "Communication" if "Communication" in skills_available else (skills_available[0] if skills_available else "")
        skill_in = st.text_input("Search any skill", value=default_skill, key="global_skill_input").strip()
        if skill_in:
            cand = [skill_in, normalise_skill(skill_in)]
            match = None
            for c in cand:
                if c in share_df.columns:
                    match = c
                    break
                ci = [col for col in share_df.columns if str(col).lower() == str(c).lower()]
                if ci:
                    match = str(ci[0])
                    break
            if match:
                sk_data = share_df[match].dropna().sort_values(ascending=False).reset_index()
                sk_data.columns = ["Country", "Share %"]
                top15 = sk_data.head(15).copy()
                top15["Type"] = top15["Country"].astype(str).map(
                    lambda x: "United Kingdom" if x == "United Kingdom" else "Other"
                )
                fig_sk = px.bar(
                    top15.sort_values("Share %"),
                    x="Share %",
                    y="Country",
                    orientation="h",
                    title=f"Top 15 by skill share — {match}",
                    color="Type",
                    color_discrete_map={"United Kingdom": TEAL, "Other": DIM},
                )
                fig_sk.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
                fig_sk.update_layout(legend_title="", yaxis_categoryorder="total ascending")
                match_skill = match
                fig_bub = None
                if match_skill and sk_data is not None and not sk_data.empty:
                    top10_bubble = sk_data.head(10).copy()
                    top10_bubble["Is_UK"] = top10_bubble["Country"].apply(
                        lambda x: "United Kingdom" if x == "United Kingdom" else "Other"
                    )

                    fig_bub = px.scatter(
                        top10_bubble,
                        x="Country",
                        y="Share %",
                        size="Share %",
                        color="Is_UK",
                        color_discrete_map={
                            "United Kingdom": "#00E5CC",
                            "Other": "#A78BFA",
                        },
                        title=f"Skill Share Bubble — {match_skill}",
                        hover_data={"Share %": ":.2f"},
                        size_max=50,
                    )
                    fig_bub.update_layout(
                        showlegend=False,
                        xaxis_tickangle=45,
                        xaxis_title="",
                        yaxis_title="Share % of Jobs",
                    )

                if fig_bub is not None:
                    c_l, c_r = st.columns(2)
                    with c_l:
                        show(fig_sk, 460)
                    with c_r:
                        show(fig_bub, 380)
                else:
                    show(fig_sk, 460)
            else:
                st.warning(f"Skill not found: `{skill_in}`. Try e.g. {', '.join(skills_available[:6])}.")

    st.subheader("UK ahead / behind the world")
    st.caption("Difference = UK share − global average share (binary % points)")
    if use_live and not share_df.empty:
        ahead, behind = compute_uk_vs_world(share_df, all_job_counts, top_n=7)
        rnk = build_rankings_table(share_df, all_job_counts, n_show=12)
        sim_pairs = cosine_similarity_to_uk(share_df, top_n=12)
    else:
        ahead, behind = STATIC_AHEAD, STATIC_BEHIND
        rnk = STATIC_RANKINGS
        sim_pairs = STATIC_SIMILAR

    ahead_plot = ahead
    behind_plot = behind

    ahead_df = pd.DataFrame(ahead_plot, columns=["Skill", "Diff"])
    behind_df = pd.DataFrame(behind_plot, columns=["Skill", "Diff"])
    behind_df["Diff"] = -behind_df["Diff"]

    combined = pd.concat([ahead_df, behind_df])
    combined = combined.sort_values("Diff")
    combined["Color"] = combined["Diff"].apply(lambda x: "UK Ahead" if x > 0 else "UK Behind")
    combined["AbsDiff"] = combined["Diff"].abs()

    fig_div = px.bar(
        combined,
        x="Diff",
        y="Skill",
        orientation="h",
        color="Color",
        color_discrete_map={
            "UK Ahead": "#34D399",
            "UK Behind": "#FF5572",
        },
        title="UK vs Global Average — Skill Share Difference (%)",
        text="AbsDiff",
    )
    fig_div.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
    )
    fig_div.add_vline(
        x=0,
        line_color="rgba(255,255,255,0.3)",
        line_width=2,
    )
    fig_div.update_layout(
        showlegend=True,
        xaxis_title="Difference from Global Average (%)",
        yaxis_title="",
        legend=dict(orientation="h", y=1.08),
    )
    show(fig_div, 500)
    st.caption(
        "Green = UK demands this skill MORE than world average · "
        "Red = UK demands this skill LESS than world average"
    )

    st.subheader("UK skill rankings vs global")
    st.dataframe(rnk, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "UK #1 Skill Globally",
        "Communication",
        "51.63% of UK gaming jobs",
    )
    col2.metric(
        "Biggest UK Advantage",
        "Talent Acquisition",
        "+13.67% above world avg",
    )
    col3.metric(
        "Biggest UK Gap",
        "CI/CD",
        "-8.25% below world avg",
    )

    st.subheader("Countries most similar to UK")
    if sim_pairs:
        df_sim = pd.DataFrame(sim_pairs, columns=["Country", "Similarity"]).sort_values("Similarity")
        fig_sim = px.bar(
            df_sim.sort_values("Similarity"),
            x="Similarity",
            y="Country",
            orientation="h",
            title="Countries Most Similar to UK Gaming Skill Profile",
            color="Similarity",
            color_continuous_scale=[
                [0.0, "#111D2E"],
                [0.5, "#0D7A8E"],
                [1.0, "#00E5CC"],
            ],
            text="Similarity",
        )
        fig_sim.update_traces(
            texttemplate="%{text:.4f}",
            textposition="outside",
            textfont=dict(size=11, color="#F0F4F8"),
        )
        fig_sim.update_layout(
            coloraxis_showscale=False,
            xaxis_range=[0.70, 1.02],
            xaxis_title="Cosine Similarity (out of 1.0)",
            yaxis_title="",
        )
        fig_sim.add_vline(
            x=1.0,
            line_color="rgba(255,255,255,0.15)",
            line_dash="dash",
            annotation_text="Perfect match = 1.0",
            annotation_font=dict(color="#8A9BB0", size=10),
        )
        show(fig_sim, 420)
        st.caption(
            "Cosine similarity measures how similar each country's "
            "gaming skill demand profile is to UK · "
            "1.0 = identical · France 0.9675 = most similar"
        )


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


STEP_D_REQUIRED_COLS = frozenset({"UK_Region", "Skill", "Demand_Count", "Gap_Score"})


def step_d_dataframe_ok(df: pd.DataFrame) -> bool:
    return df is not None and not df.empty and STEP_D_REQUIRED_COLS.issubset(df.columns)


def _norm_skill_token(s: object) -> str:
    return str(s).strip().lower().replace(" ", "-").replace("_", "-")


def cv_text_covers_skill_token(cv_found_slugs: set[str], skill_label: object) -> bool:
    """True if Step C/D skill label matches a slug detected on the CV (fuzzy on spaces/hyphens)."""
    t = _norm_skill_token(skill_label)
    if not t:
        return False
    if t in cv_found_slugs:
        return True
    if t.replace("-", "") in {x.replace("-", "") for x in cv_found_slugs}:
        return True
    for slug in cv_found_slugs:
        if slug == t or slug.replace("-", "") == t.replace("-", ""):
            return True
    return False


def top_gap_skills_not_in_cv(
    df_c: pd.DataFrame, region: str, found_slugs: set[str], n: int = 5
) -> list[tuple[str, float]]:
    """High-gap Step C skills in `region` whose slugs were not detected on the CV."""
    if df_c is None or df_c.empty:
        return []
    need = {"UK Region", "Skills", "Gap_Score"}
    if not need.issubset(df_c.columns):
        return []
    sub = df_c[df_c["UK Region"].astype(str).str.strip() == region].copy()
    if sub.empty:
        return []
    sub = sub.sort_values("Gap_Score", ascending=False)
    out: list[tuple[str, float]] = []
    for _, r in sub.iterrows():
        sk = str(r["Skills"]).strip().lower()
        if sk in found_slugs:
            continue
        out.append((cn(sk), float(r["Gap_Score"])))
        if len(out) >= n:
            break
    return out


def top_workshop_skills_not_in_cv(
    df_d: pd.DataFrame, region: str, found_slugs: set[str], n: int = 3
) -> list[str]:
    if not step_d_dataframe_ok(df_d):
        return []
    sub = df_d[df_d["UK_Region"].astype(str).str.strip() == region].copy()
    if sub.empty:
        return []
    sub = sub.sort_values("Gap_Score", ascending=False)
    out: list[str] = []
    for _, r in sub.iterrows():
        if cv_text_covers_skill_token(found_slugs, r["Skill"]):
            continue
        out.append(str(r["Skill"]).strip())
        if len(out) >= n:
            break
    return out


def uk_vs_global_skill_table(gdf: pd.DataFrame, n_show: int = 12) -> pd.DataFrame | None:
    """UK vs world skill shares and ranks from live gaming rows (exploded comma skills)."""
    if gdf is None or gdf.empty or "Skills" not in gdf.columns or "Country" not in gdf.columns:
        return None
    uk_mask = _is_uk_country_mask(gdf["Country"])
    uk = gdf.loc[uk_mask]
    n_uk = int(len(uk))
    n_w = int(len(gdf))
    if n_uk < 1 or n_w < 1:
        return None
    long_w = explode_job_skills(gdf)
    long_u = explode_job_skills(uk)
    if long_w.empty:
        return None
    wc = long_w.groupby("Skill").size()
    uc = long_u.groupby("Skill").size()
    skills_all = wc.index.union(uc.index)
    uk_rates = {s: float(uc.get(s, 0)) / n_uk * 100.0 for s in skills_all}
    world_rates = {s: float(wc.get(s, 0)) / n_w * 100.0 for s in skills_all}
    uk_order = sorted(skills_all, key=lambda s: -uk_rates[s])
    world_order = sorted(skills_all, key=lambda s: -world_rates[s])
    r_uk = {s: i + 1 for i, s in enumerate(uk_order)}
    r_w = {s: i + 1 for i, s in enumerate(world_order)}
    display_skills = list(wc.nlargest(n_show).index)
    rows: list[list[object]] = []
    for sk in display_skills:
        ur = uk_rates[sk]
        wr = world_rates[sk]
        if ur > wr + 0.05:
            trend = "↑ Ahead"
        elif ur < wr - 0.05:
            trend = "↓ Behind"
        else:
            trend = "≈ Parity"
        rows.append(
            [
                cn(str(sk)),
                round(ur, 2),
                r_uk[sk],
                round(wr, 2),
                r_w[sk],
                trend,
            ]
        )
    return pd.DataFrame(
        rows,
        columns=["Skill", "UK Share %", "UK Rank", "Global Avg %", "Global Rank", "Trend"],
    )


def country_cosine_similarity_to_uk(
    gdf: pd.DataFrame, top_n: int = 50, max_countries: int = 12
) -> tuple[list[tuple[str, float]], str | None]:
    """Cosine similarity of per-country skill mention-rate vectors vs UK (same vocabulary)."""
    long = explode_job_skills(gdf)
    if long.empty or "Country" not in gdf.columns:
        return [], None
    vc = long["Skill"].value_counts()
    if vc.empty:
        return [], None
    skill_vocab = list(vc.head(min(top_n, int(vc.shape[0]))).index)
    if not skill_vocab:
        return [], None
    skill_i = {s: i for i, s in enumerate(skill_vocab)}
    countries = gdf["Country"].astype(str).str.strip()
    n_by = gdf.groupby(countries).size()
    country_list = [c for c in n_by.index.astype(str)]
    mat = np.zeros((len(country_list), len(skill_vocab)), dtype=float)
    cidx = {c: i for i, c in enumerate(country_list)}
    for _, r in long.iterrows():
        co = str(r["Country"]).strip()
        sk = r["Skill"]
        if sk not in skill_i or co not in cidx:
            continue
        mat[cidx[co], skill_i[sk]] += 1.0
    for i in range(len(country_list)):
        d = float(n_by.iloc[i])
        if d <= 0:
            d = 1.0
        mat[i, :] /= d
    uk_key: str | None = None
    for co in country_list:
        if bool(_is_uk_country_mask(pd.Series([co])).iloc[0]):
            uk_key = co
            break
    if uk_key is None or uk_key not in cidx:
        return [], None
    u = mat[cidx[uk_key]]
    nu = float(np.linalg.norm(u))
    out: list[tuple[str, float]] = []
    for i, co in enumerate(country_list):
        if co == uk_key:
            continue
        v = mat[i]
        nv = float(np.linalg.norm(v))
        if nu <= 0 or nv <= 0:
            continue
        sim = float(np.dot(u, v) / (nu * nv))
        out.append((co, sim))
    out.sort(key=lambda x: -x[1])
    return out[:max_countries], uk_key


def step_c_row_counts_by_region(df_c: pd.DataFrame) -> dict[str, int]:
    """Step C row counts per UK region (one row ≈ one skill line in that region)."""
    if df_c is None or df_c.empty or "UK Region" not in df_c.columns:
        return {}
    sub = df_c.copy()
    sub["_reg"] = sub["UK Region"].astype(str).str.strip()
    return sub.groupby("_reg").size().astype(int).to_dict()


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

# ── Sidebar navigation (no footer attribution block) ─────────────────────────
NAV_OPTIONS = [
    "📊 UK & Regions",
    "🤖 AI Gaps",
    "🌍 Global",
    "📄 CV",
]
with st.sidebar:
    st.markdown(
        """
<div style="margin:0 0 2px 0;">
  <span style="font-size:1.35rem;font-weight:700;color:#F0F4F8;letter-spacing:-0.02em;">
    🎮 Skill Intelligence
  </span>
</div>
<div style="width:52px;height:3px;border-radius:2px;margin:10px 0 14px 0;
  background:linear-gradient(90deg,#00E5CC 0%,#A78BFA 100%);"></div>
<div style="font-size:0.82rem;color:#94A3B8;font-weight:600;margin:0 0 4px 0;">
  UK Gaming Industry
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div style="font-size:10px;color:#64748B;text-transform:uppercase;
letter-spacing:2px;font-weight:600;margin:14px 0 10px 0;">Navigate</div>
""",
        unsafe_allow_html=True,
    )
    tab = st.radio(
        "Section",
        NAV_OPTIONS,
        label_visibility="collapsed",
        key="main_nav_radio",
    )

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
    with st.expander("Metric definitions (how to read this tab)", expanded=False):
        st.markdown(
            """
- **Total job ads** — Unique job listings in the UK gaming sample (1,121); Step A stores one row per skill per ad.
- **Skill rows / mentions** — One row per skill tag attached to a listing in Step A.
- **Per 100k** — Skill counts divided by national population × 100,000, so regions are comparable.
- **Regional top tile** — Highest-demand skill in each region among its top five by count, as mentions per 100k (same rule for all four).
- **Demo / fallback** — If a CSV is missing, some charts use built-in sample data (Step A–D files
  under `Step files/`).
            """.strip()
        )

    if uk_sub == "UK Overview":
        n_rows = len(df_a)
        n_jobs = UK_OVERVIEW_TOTAL_JOB_ADS
        n_skills = UK_OVERVIEW_UNIQUE_SKILLS
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

        st.markdown(f"#### UK Overview · `{n_jobs:,} total job ads`")
        st.caption(
            f"{n_jobs:,} job ads · {n_rows:,} skill rows · source: {src}"
        )

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Job Ads", f"{n_jobs:,}", "Unique job listings")
        k2.metric("Unique Skills", f"{n_skills:,}", "Distinct skill tokens")
        k3.metric("Skill Rows", f"{n_rows:,}", "After cleaning in pipeline")
        k4.metric("UK Regions", str(n_regions), "ENG · SCO · WAL · NI")

        st.markdown("---")
        st.subheader("Top 15 skills by demand")
        st.caption(f"Occurrences in Step A — {n_rows:,} skill rows")
        if len(vc15):
            df_top = pd.DataFrame(
                {"Skill": [cn(str(s)) for s in vc15.index], "Count": vc15.values.astype(int)}
            )
            denom = n_rows if n_rows > 0 else 1
            df_top["Share_pct"] = (df_top["Count"] / denom * 100).round(1)
            df_sorted = df_top.sort_values("Count")
            fig_ov = px.bar(
                df_sorted,
                x="Count",
                y="Skill",
                orientation="h",
                title="Skill occurrences",
                color_discrete_sequence=[TEAL],
            )
            fig_ov.update_layout(showlegend=False, yaxis_categoryorder="total ascending")
            fig_ov.update_traces(
                texttemplate="%{x:,}",
                textposition="outside",
                hovertext=[
                    f"Count={int(c):,}<br>{float(p):.1f}% of {n_rows:,} skill rows"
                    for c, p in zip(df_sorted["Count"], df_sorted["Share_pct"])
                ],
                hovertemplate="<b>%{y}</b><br>%{hovertext}<extra></extra>",
            )
            show(fig_ov, 460)
        else:
            st.warning("No skills in the current dataset.")

        st.markdown("---")
        st.subheader("Skill Demand Over Time")
        st.caption(
            "Monthly skill mentions · Jul–Oct 2025 · "
            "Step A data · select skills to compare"
        )
        if "Activated Date" not in df_a.columns:
            st.warning("Date column not available for time series analysis")
        elif "Skills" not in df_a.columns:
            st.warning("Date column not available for time series analysis")
        else:
            a_ts = df_a.copy()
            a_ts["Activated Date"] = pd.to_datetime(
                a_ts["Activated Date"], errors="coerce"
            )
            if int(a_ts["Activated Date"].notna().sum()) == 0:
                st.warning("Date column not available for time series analysis")
            else:
                a_ts["Month"] = a_ts["Activated Date"].dt.to_period("M").astype(str)
                if "Skill_Display" not in a_ts.columns:
                    a_ts["Skill_Display"] = a_ts["Skills"].map(lambda x: cn(str(x)))
                top10_skills = (
                    a_ts["Skill_Display"]
                    .value_counts()
                    .head(10)
                    .index.tolist()
                )
                if not top10_skills:
                    st.warning("Date column not available for time series analysis")
                else:
                    selected_skills = st.multiselect(
                        "Select skills to compare:",
                        options=top10_skills,
                        default=top10_skills[:5],
                        key="ts_skills",
                    )
                    if selected_skills:
                        ts_df = (
                            a_ts[a_ts["Skill_Display"].isin(selected_skills)]
                            .groupby(["Month", "Skill_Display"])
                            .size()
                            .reset_index(name="Mentions")
                            .sort_values("Month")
                        )
                        fig_ts = px.line(
                            ts_df,
                            x="Month",
                            y="Mentions",
                            color="Skill_Display",
                            markers=True,
                            title="Skill Demand by Month — UK Gaming Industry",
                            labels={
                                "Month": "Month",
                                "Mentions": "Skill Mentions",
                                "Skill_Display": "Skill",
                            },
                            color_discrete_sequence=[
                                "#00E5CC",
                                "#A78BFA",
                                "#34D399",
                                "#F5A623",
                                "#60A5FA",
                                "#FF5572",
                                "#FB923C",
                                "#FCD34D",
                                "#F472B6",
                                "#818CF8",
                            ],
                        )
                        fig_ts.update_traces(line_width=2.5, marker_size=8)
                        fig_ts.update_layout(
                            hovermode="x unified",
                            legend=dict(orientation="h", y=-0.2),
                        )
                        show(fig_ts, 420)
                        st.info(
                            "Communication remained the most demanded skill across all months confirming it is "
                            "sustained employer demand not a seasonal spike."
                        )
                    else:
                        st.caption("Select at least one skill to plot the time series.")

    else:
        regional, z_hm, x_hm, y_hm = compute_regional_tables(df_a)

        if not regional:
            regional = {
                "England": [("—", 0, 0.0)],
                "Scotland": [("—", 0, 0.0)],
                "Wales": [("—", 0, 0.0)],
                "N. Ireland": [("—", 0, 0.0)],
            }
        def _top_regional_row(reg_name: str) -> tuple[str, int, float]:
            rows = regional.get(reg_name, [])
            if rows:
                return rows[0]
            return ("—", 0, 0.0)

        eng = _top_regional_row("England")
        sco = _top_regional_row("Scotland")
        wal = _top_regional_row("Wales")
        n_ir = _top_regional_row("N. Ireland")

        st.markdown("#### Regional Analysis · `4 Regions`")
        st.caption(
            "England · Scotland · Wales · N. Ireland — per 100k · Step A · Step B clusters"
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("England — top /100k", f"{eng[2]:.2f}", str(eng[0]))
        c2.metric("Scotland — top /100k", f"{sco[2]:.2f}", str(sco[0]))
        c3.metric("Wales — top /100k", f"{wal[2]:.2f}", str(wal[0]))
        c4.metric("N. Ireland — top /100k", f"{n_ir[2]:.2f}", str(n_ir[0]))

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
        hm_live = bool(z_hm and x_hm and y_hm)
        if hm_live:
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
            st.warning(
                "**Demo heatmap** — Step A has no usable regional heatmap (missing file, empty data, "
                "or required columns). Values below are static placeholders, not your CSV."
            )
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

        st.markdown("---")
        st.subheader("Cluster profile radar (per 100k)")
        st.caption("Six Step B clusters plotted for all four UK regions (reference profile).")

        clusters = ["Game Dev", "Soft Skills", "Proj Mgmt", "Creative", "Biz Tools", "Cloud"]
        _theta = clusters + [clusters[0]]
        radar = {
            "England": [3.55, 3.55, 1.49, 1.45, 0.72, 0.71],
            "Scotland": [2.19, 1.60, 0.93, 0.44, 0.47, 0.18],
            "Wales": [1.06, 0.47, 0.09, 0.16, 0.22, 0.28],
            "N. Ireland": [1.88, 1.20, 0.58, 0.21, 0.37, 0.00],
        }
        radar_cols = {
            "England": "#60A5FA",
            "Scotland": "#34D399",
            "Wales": "#F5A623",
            "N. Ireland": "#A78BFA",
        }

        fig_r = go.Figure()
        for region, vals in radar.items():
            r = list(vals) + [vals[0]]
            fig_r.add_trace(
                go.Scatterpolar(
                    r=r,
                    theta=_theta,
                    mode="lines+markers",
                    name=region,
                    line=dict(color=radar_cols.get(region, TEAL), width=2),
                    marker=dict(size=6),
                )
            )
        fig_r.update_layout(
            title="Regions × clusters — per 100k",
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True,
                    gridcolor="rgba(255,255,255,0.06)",
                    tickcolor="rgba(255,255,255,0.12)",
                ),
                angularaxis=dict(
                    gridcolor="rgba(255,255,255,0.06)",
                    tickcolor="rgba(255,255,255,0.12)",
                ),
            ),
            showlegend=True,
            legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        )
        show(fig_r, 460, margin_patch=dict(t=40, b=90), axis_tick_color="#CBD5E1")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI GAP ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "🤖 AI Gaps":
    n_gap = len(df_c)
    n_rec = len(df_d)
    n_a_rows = len(df_a)
    # Same verified distinct-skill total as UK Overview (not raw CSV nunique — can differ slightly).
    n_a_skills = UK_OVERVIEW_UNIQUE_SKILLS
    n_cl = int(df_c["Cluster_Name"].nunique()) if live_c and "Cluster_Name" in df_c.columns else 6

    st.markdown(f"#### AI Gap Analysis · `{n_gap} gap rows`")
    st.caption(
        f"TF-IDF · K-Means · LQ gaps · workshops · Step C {n_gap} rows · Step D {n_rec} recs"
    )
    with st.expander("Suggested reading order", expanded=False):
        st.markdown(
            "1. Cluster stack and region × cluster heatmap — where pressure sits.  \n"
            "2. Workshop recommendation table — concrete priorities.  \n"
            "3. Pick a **UK region** below — skill-level demand vs gap bars."
        )

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
        if z_gh and x_gh and y_gh:
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
        else:
            st.warning(
                "Region × cluster gap heatmap needs **Step C** data: load `step_c_gap_scores.csv` with columns "
                "**UK Region**, **Cluster_Name**, and **Gap_Score** (numeric). "
                "Values are the **mean Gap_Score** per region × cluster from that file."
            )
            if not live_c:
                st.caption(
                    "Step C CSV was not found — place `step_c_gap_scores.csv` in the project or `Step files/` folder."
                )

    with col_r:
        st.caption("Workshop recommendations")
        st.caption("Step D output — ranked by gap score · priority coded")
        if live_d and not step_d_dataframe_ok(df_d):
            st.error(
                "Step D file is loaded but required columns are missing. Expected at least: "
                f"`{', '.join(sorted(STEP_D_REQUIRED_COLS))}`. Showing demo workshop table until the CSV matches."
            )
        if step_d_dataframe_ok(df_d):
            df_d_display = df_d.copy()
            df_d_display["UK Region"] = df_d_display["UK_Region"].astype(str).str.strip()
            df_d_display["Skills"] = df_d_display["Skill"].map(lambda s: _norm_skill_token(s))
            if (
                len(df_c)
                and "Supply" in df_c.columns
                and "UK Region" in df_c.columns
                and "Skills" in df_c.columns
            ):
                supply_lookup = df_c[["UK Region", "Skills", "Supply"]].copy()
                supply_lookup = supply_lookup.drop_duplicates(
                    subset=["UK Region", "Skills"], keep="first"
                )
                df_d_display = df_d_display.merge(
                    supply_lookup,
                    on=["UK Region", "Skills"],
                    how="left",
                )
            else:
                df_d_display["Supply"] = np.nan
            df_d_display["Supply"] = (
                pd.to_numeric(df_d_display["Supply"], errors="coerce").round(4).fillna(0.0)
            )
            cluster_col = (
                "Cluster_Name"
                if "Cluster_Name" in df_d_display.columns
                else ("Skill_Cluster" if "Skill_Cluster" in df_d_display.columns else None)
            )
            pri = (
                df_d_display["Workshop_Recommendation"].map(_prior_from_rec)
                if "Workshop_Recommendation" in df_d_display.columns
                else "—"
            )
            ws_df = pd.DataFrame(
                {
                    "UK Region": df_d_display["UK Region"],
                    "Skills": df_d_display["Skill"],
                    "Cluster_Name": df_d_display[cluster_col] if cluster_col else "—",
                    "Demand": df_d_display["Demand_Count"].astype(int),
                    "Supply": df_d_display["Supply"],
                    "Gap_Score": pd.to_numeric(df_d_display["Gap_Score"], errors="coerce"),
                    "Priority": pri,
                }
            )
        else:
            ws_df = pd.DataFrame(
                WORKSHOP_HTML,
                columns=["UK Region", "Skills", "Demand", "Gap_Score", "Priority"],
            )
            ws_df["Gap_Score"] = ws_df["Gap_Score"].map(lambda x: float(x))
            ws_df["Cluster_Name"] = "—"
            ws_df["Supply"] = 0.0
            ws_df = ws_df[
                [
                    "UK Region",
                    "Skills",
                    "Cluster_Name",
                    "Demand",
                    "Supply",
                    "Gap_Score",
                    "Priority",
                ]
            ]
        st.dataframe(ws_df, use_container_width=True, hide_index=True)
        st.caption(
            "Supply = Location Quotient scaled 0–10 · "
            "Low Supply + High Demand = High Gap Score · "
            "Communication Supply 0.1759 is near zero "
            "confirming maximum urgency"
        )

    c_row_counts = step_c_row_counts_by_region(df_c) if len(df_c) and "UK Region" in df_c.columns else {}
    thin = [
        f"{reg} ({c_row_counts[reg]} rows)"
        for reg in ("Wales", "Northern Ireland")
        if c_row_counts.get(reg, 0) > 0 and c_row_counts.get(reg, 0) < 25
    ]
    if thin:
        st.caption(
            "Small Step C samples for some regions can make gap scores noisy; treat Wales / N.Ireland "
            f"cells with extra caution when row counts are low ({'; '.join(thin)})."
        )

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
    k3.metric("Top workshop skill", str(ws_df.iloc[0]["Skills"]) if len(ws_df) else "—", "1st row Step D")
    k4.metric("Clusters (Step C)", str(n_cl), "Distinct cluster names")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — GLOBAL COMPARISON
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "🌍 Global":
    render_global_tab(df_global, source_name=global_source_name)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5 — CV EVALUATOR
# ═════════════════════════════════════════════════════════════════════════════
elif tab == "📄 CV":
    st.markdown("#### CV Evaluator · `Step A–aligned`")
    st.caption(
        "Lexical match vs **Step A** tokens · paste or PDF — same UK gaming rows as the dashboard"
    )
    with st.expander("How matching works · privacy", expanded=False):
        st.markdown(
            "**Lexical only** — Exact tokens and aliases (e.g. C++, CI/CD). No inference from job titles "
            "or paraphrases; wording that appears in your Step A data works best.  \n\n"
            "**Privacy** — CV text stays in this browser session; not sent to an external API."
        )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**📤 Input**\n\nPaste or upload PDF/TXT")
    with c2:
        st.markdown("**🔍 Detect skills**\n\nWord-boundary match + aliases")
    with c3:
        st.markdown(
            f"**📊 Match dataset**\n\n{UK_OVERVIEW_TOTAL_JOB_ADS:,} total job ads · "
            f"{UK_OVERVIEW_UNIQUE_SKILLS:,} skill tokens"
        )
    with c4:
        st.markdown("**💡 Feedback**\n\nDemand + listing reach + gaps")

    cv_gap_region = st.selectbox(
        "UK region for gap cross-check",
        ["England", "Scotland", "Wales", "Northern Ireland"],
        index=0,
        key="cv_gap_region_select",
        help="Highlights high-gap skills from Step C / Step D for this region that your CV did not match.",
    )
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

    if st.button("Analyse My CV", type="primary"):
        if not cv_text.strip():
            st.warning("Please paste your CV text first.")
        else:
            vocab = _cv_vocab_from_step_a(df_a)
            vocab_set = set(vocab)
            found = _cv_detect_skills(cv_text, vocab)
            found_set = set(found)
            top_p = _cv_top_priority_skills(df_a, 10)
            miss = [s for s in top_p if s not in found_set]
            mention_pct = _cv_demand_weighted_pct(df_a, found_set)
            list_pct, list_hits, list_n = _cv_listing_overlap(df_a, found_set)
            cov_pct = round(len(found) / len(vocab) * 100, 1) if vocab else 0.0
            scores = _cv_category_scores(found_set, vocab_set)
            if not scores:
                scores = [("—", 0.0, 0, 0)]

            with st.expander("Text used for matching (check PDF/OCR quality)", expanded=False):
                st.text(cv_text[:6000] + ("…" if len(cv_text) > 6000 else ""))

            st.subheader("Your analysis results")
            st.caption(
                f"Step A: **{'live CSV' if live_a else 'demo sample'}** · vocabulary = distinct tokens in file"
            )

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Skills matched", str(len(found)), f"of {len(vocab)} in dataset · {cov_pct}% coverage")
            c2.metric(
                "Dataset mention %",
                f"{mention_pct}%",
                "Share of all skill rows that hit your CV tokens",
            )
            c3.metric(
                "Listing reach",
                f"{list_pct}%",
                f"{list_hits} / {list_n} listing groups share ≥1 skill",
            )
            c4.metric("Priority gaps", str(len(miss)), "Top Step A skills not detected")

            cl, cr = st.columns(2)
            with cl:
                st.caption(f"{len(found)} skills from the Step A vocabulary detected in your CV")
                if found:
                    st.success(" · ".join(cn(s) for s in found))
                else:
                    st.caption("No vocabulary matches — try exact tool names from job ads in your file.")
                st.markdown("**Missing high-demand skills (Step A top 10)**")
                st.caption("Frequent tokens in your loaded dataset that did not match your CV")
                if miss:
                    st.error(" · ".join(cn(s) for s in miss))
                else:
                    st.success("You cover the current top-10 demand tokens.")
            with cr:
                st.caption(
                    "Role-family scores — only skills that exist **both** in Step A and each category list"
                )
                df_cm = pd.DataFrame(
                    [(c, s, m, t) for c, s, m, t in scores],
                    columns=["Category", "Score %", "Matched", "Total"],
                ).sort_values("Score %", ascending=True)
                fig_cm = px.bar(
                    df_cm,
                    x="Score %",
                    y="Category",
                    orientation="h",
                    title="Job category match (dataset-scoped)",
                    color="Score %",
                    color_continuous_scale=[[0, RED], [0.4, AMBER], [1, GREEN]],
                )
                fig_cm.update_traces(texttemplate="%{x:.0f}%", textposition="outside")
                fig_cm.update_layout(coloraxis_showscale=False)
                show(fig_cm, 380)

            st.subheader("Top job recommendations")
            st.caption("Highest category coverage (after dataset filter)")
            t1, t2, t3 = st.columns(3)
            for i, (cat, score, matched, total) in enumerate(scores[:3]):
                col = (t1, t2, t3)[i]
                with col:
                    st.metric(cat, f"{score:.0f}%", f"{matched} of {total} skills")

            if not found:
                advice = (
                    "No Step A skill tokens matched. Use wording that appears in your job dataset "
                    "(e.g. Unity, Python, C++, communication) or paste cleaner text if the PDF was scanned."
                )
            elif mention_pct >= 35 or list_pct >= 50:
                advice = (
                    f"Strong overlap with loaded UK rows ({mention_pct}% of skill mentions · "
                    f"{list_pct}% of listing groups). Best category: **{scores[0][0]}**. "
                    f"Next: add {cn(miss[0]) if miss else 'depth on your strongest stack'} if still missing from top demand."
                )
            elif mention_pct >= 15 or list_pct >= 25:
                advice = (
                    f"Moderate fit. Adding {', '.join(cn(s) for s in miss[:3])} would align you with "
                    f"the most common tokens in this Step A file."
                )
            else:
                advice = (
                    f"Low overlap with current listings. Prioritise: {', '.join(cn(s) for s in miss[:4])} "
                    f"— these are among the most repeated skills in the loaded dataset."
                )
            st.info(f"💡 **Career advice** — {advice}")

            miss_gaps = top_gap_skills_not_in_cv(df_c, cv_gap_region, found_set, n=5)
            miss_ws = top_workshop_skills_not_in_cv(df_d, cv_gap_region, found_set, n=3)
            with st.expander(
                f"🔗 AI Gap tab — high-priority skills for **{cv_gap_region}** you did not match",
                expanded=False,
            ):
                st.caption(
                    "Same signals as **AI Gaps**: Step C = gap score; Step D = workshop recommender. "
                    "Add honest keywords to your CV if these truly apply."
                )
                if miss_gaps:
                    lines = [f"- **{s}** (gap score {g:.2f})" for s, g in miss_gaps]
                    st.markdown("**From Step C (top gaps not on your CV)**\n" + "\n".join(lines))
                else:
                    st.caption("No extra Step C gap rows for this region, or your CV already covers the top gaps.")
                if miss_ws:
                    st.markdown(
                        "**From Step D (workshop picks not on your CV)**\n"
                        + "\n".join(f"- {s}" for s in miss_ws)
                    )
                elif step_d_dataframe_ok(df_d):
                    st.caption("Step D has no extra workshop skills for this region that you are missing.")
                else:
                    st.caption("Step D file missing or wrong columns — open **AI Gaps** after fixing `step_d_workshop_recommendations.csv`.")

            st.markdown("---")
            st.subheader("Matching Job Listings — UK Gaming Dataset")
            st.caption(
                "Jobs from the UK gaming dataset that match "
                "your detected skills · sorted by most recent date"
            )

            matched_jobs = match_jobs_to_cv(
                df_a,
                found,
                df_global=df_global,
                top_n=500,
            )

            if not matched_jobs.empty:

                table_df = matched_jobs
                if "UK Region" in matched_jobs.columns:
                    _regions = (
                        matched_jobs["UK Region"]
                        .dropna()
                        .astype(str)
                        .str.strip()
                        .replace("", pd.NA)
                        .dropna()
                        .unique()
                        .tolist()
                    )
                    _regions = sorted(_regions)
                    region_pick = st.selectbox(
                        "Filter matched jobs by UK region",
                        ["All regions"] + _regions,
                        index=0,
                        key="cv_match_jobs_region_filter",
                    )
                    if region_pick != "All regions":
                        table_df = matched_jobs[
                            matched_jobs["UK Region"].astype(str).str.strip() == region_pick
                        ].copy()

                # Keep the display compact, but ensure region filtering has enough rows to work with.
                display_limit = 20
                table_show = table_df.head(display_limit).copy()

                st.success(
                    f"Found {len(table_df)} job listings "
                    f"matching your skills from the UK gaming dataset "
                    f"(showing top {min(display_limit, len(table_df))})"
                )

                if "Job Role" not in matched_jobs.columns:
                    st.caption(
                        "Job role titles not available — "
                        "check Combined Data workbook has "
                        "a Title or Role column"
                    )

                if "Apply Link" not in matched_jobs.columns:
                    st.caption(
                        "Apply links not available — "
                        "check Combined Data workbook has "
                        "a Link or URL column"
                    )

                # Top 3 metric cards
                top3 = table_show.head(3)
                c1, c2, c3 = st.columns(3)
                for col, (_, row) in zip([c1, c2, c3], top3.iterrows()):
                    col.metric(
                        label="Skills matched",
                        value=f"{int(row['Skills_Matched'])} skills",
                        delta=str(row.get("UK Region", "")),
                    )

                # Display table
                display_cols = [
                    c
                    for c in ["Job Role", "UK Region", "Skills_Matched", "Activated Date", "Apply Link"]
                    if c in table_show.columns
                ]

                # Rename Skills_Matched for display
                display_df = table_show[display_cols].copy()

                # Configure columns
                col_config = {
                    "Skills_Matched": st.column_config.NumberColumn(
                        "Skills Matched",
                        help="Number of your CV skills found in this job",
                    ),
                    "Activated Date": st.column_config.DateColumn(
                        "Date Posted",
                        format="DD/MM/YYYY",
                    ),
                }

                # Add link column config if it exists
                if "Apply Link" in display_df.columns:
                    col_config["Apply Link"] = st.column_config.LinkColumn(
                        "Apply",
                        help="Click to apply for this job",
                        display_text="Apply Now",
                    )

                if "Job Role" in display_df.columns:
                    col_config["Job Role"] = st.column_config.TextColumn(
                        "Job Role",
                        width="medium",
                    )

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=col_config,
                )

                # Bar chart by region
                if "UK Region" in table_df.columns:
                    region_counts = table_df["UK Region"].value_counts().reset_index()
                    region_counts.columns = ["Region", "Jobs"]

                    fig_match = px.bar(
                        region_counts,
                        x="Jobs",
                        y="Region",
                        orientation="h",
                        title="Matching jobs by UK region",
                        color="Jobs",
                        color_continuous_scale=[[0, "#111D2E"], [1, "#00E5CC"]],
                    )
                    fig_match.update_layout(coloraxis_showscale=False, height=280)
                    show(fig_match, 280)

            else:
                st.info(
                    "No exact skill matches found in the dataset. "
                    "Try adding more gaming-specific skills to your CV."
                )

            st.markdown("---")
            st.subheader("Live Job Listings")
            st.caption("Real gaming jobs matched to your skills")

            reed_key = None
            try:
                reed_key = st.secrets.get("REED_API_KEY")
            except Exception:
                pass

            if reed_key and found:
                import requests

                search_query = " ".join(list(found)[:3]) + " games"

                try:
                    resp = requests.get(
                        "https://www.reed.co.uk/api/1.0/search",
                        params={
                            "keywords": search_query,
                            "locationName": "United Kingdom",
                            "resultsToTake": 10,
                        },
                        auth=(reed_key, ""),
                        timeout=10,
                    )

                    if resp.status_code == 200:
                        live_jobs = resp.json().get("results", [])

                        if live_jobs:
                            st.success(f"Found {len(live_jobs)} live jobs " f"matching your top skills")
                            for job in live_jobs:
                                with st.expander(
                                    f"{job.get('jobTitle', 'Role')} " f"— {job.get('employerName', '')}"
                                ):
                                    col_a, col_b = st.columns(2)
                                    col_a.write(f"Location: " f"{job.get('locationName', '')}")
                                    col_b.write(f"Posted: {job.get('date', '')}")
                                    desc = job.get("jobDescription", "")
                                    if desc:
                                        st.write(desc[:300] + "...")
                                    url = job.get("jobUrl", "")
                                    if url:
                                        st.markdown(f"[Apply on Reed]({url})")
                        else:
                            st.info("No live jobs found for your skills right now.")
                    else:
                        st.warning("Could not reach Reed API right now.")

                except Exception as e:
                    st.warning(f"Live job search unavailable: {str(e)[:80]}")

            else:
                st.info(
                    "To enable live job listings add your Reed API key "
                    "to .streamlit/secrets.toml as REED_API_KEY. "
                    "Get a free key at reed.co.uk/developers"
                )

