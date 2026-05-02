# GC_dashboard — Complete Codebase Guide for Beginners

## 📚 Table of Contents

1. [What This App Does](#what-this-app-does)
2. [How to Read This Guide](#how-to-read-this-guide)
3. [The Big Picture: App Architecture](#the-big-picture-app-architecture)
4. [Starting Point: app.py](#starting-point-apppy)
5. [Data Loading Pipeline](#data-loading-pipeline)
6. [The Four Main Tabs](#the-four-main-tabs)
7. [Key Helper Functions](#key-helper-functions)
8. [Data Structures & Flow](#data-structures--flow)
9. [Supporting Files](#supporting-files)
10. [Common Tasks & Where to Find Them](#common-tasks--where-to-find-them)

---

## What This App Does

**GC_dashboard** is a Streamlit web application that analyzes **UK gaming industry skill demand**. 

**In plain English:**
- It collects job postings from gaming companies in the UK
- It extracts the skills mentioned in those jobs
- It shows you which skills are most wanted, by region, and where there are gaps
- It lets you upload your CV to see how your skills match what the industry wants
- It compares UK skill demand to other countries globally

**The app has 4 main sections (tabs):**
1. **UK & Regions** — What skills are most in demand across the UK?
2. **AI Gaps** — Which skills are most needed but hardest to find?
3. **Global** — How does UK gaming skill demand compare to the rest of the world?
4. **CV Evaluator** — Upload your CV to see how you match with job listings

---

## How to Read This Guide

**You don't need to understand everything at once.** Each section builds on the previous one.

**Quick paths through this guide:**
- **Just want to run it?** Jump to [Starting Point: app.py](#starting-point-apppy)
- **Want to understand data flow?** Read [Data Loading Pipeline](#data-loading-pipeline) → [The Four Main Tabs](#the-four-main-tabs)
- **Want to modify the code?** Read [Common Tasks & Where to Find Them](#common-tasks--where-to-find-them)
- **Want the full picture?** Read everything in order

---

## The Big Picture: App Architecture

### How the App Works (Step-by-Step)

```
START: User opens app in browser
  ↓
Step 1: Load data files from disk
  - Step A: Raw skill inventory (CSV)
  - Step B: Clustered skills (CSV)
  - Step C: Gap analysis scores (CSV)
  - Step D: Workshop recommendations (CSV)
  - Global workbook (Excel)
  ↓
Step 2: Show sidebar with 4 navigation buttons
  - User clicks one of: "UK & Regions" | "AI Gaps" | "Global" | "CV Evaluator"
  ↓
Step 3: Render chosen tab
  - Each tab loads data from Step 1
  - Displays charts, tables, metrics
  - May accept user input (date selection, text upload, etc.)
  ↓
Step 4: User sees results
  - Charts update in real-time
  - If Step A–D CSVs are missing → built-in demo sample for those tabs
  - If the global workbook is missing (e.g. on Streamlit Cloud) → Global tab shows an upload prompt, not placeholder country charts
  ↓
END: User closes app
```

### File Structure (After Restructuring)

```
GC_dashboard/
├── app.py                          ← Main Streamlit app (~3,100+ lines)
│
├── src/                            ← Helper Python modules
│   ├── __init__.py
│   ├── city_to_country_tab5.py     ← Map cities to countries
│   └── preprocess_combined_for_global.py  ← Clean global workbook
│
├── data/                           ← All data files
│   ├── steps/                      ← Step A-D CSVs
│   │   ├── step_a_clean_output.csv
│   │   ├── step_b_clustered_skills (2).csv
│   │   ├── step_c_gap_scores.csv
│   │   └── step_d_workshop_recommendations.csv
│   ├── universal_skills.csv
│   └── Updated_27_02_26_-_Kabilan.xlsx  ← Global data
│
├── assets/                         ← Images (not used in app)
│   ├── expr_charts/
│   ├── stage3_charts/
│   └── *.png files
│
└── archive/                        ← Old code
    └── app_legacy.py
```

---

## Starting Point: app.py

### What is app.py?

`app.py` is the **main file that runs when you type `streamlit run app.py`**. It contains:
- All the page setup and styling
- Functions to load data from CSV/Excel files
- Functions to create charts and tables
- The sidebar navigation menu
- All 4 tabs and their content

### How to Run It

```bash
# From the project root (C:\Users\kabil\Downloads\GC_dashboard):
streamlit run app.py

# Then open http://localhost:8501 in your browser
```

### Understanding the Structure of app.py

The file is organized in sections (marked with `# ── Section Name ──`):

| Lines | Section | What's Happening |
|-------|---------|-----------------|
| 1-15 | Imports | Load Python libraries (pandas, plotly, streamlit, etc.) |
| 17-35 | Page Config | Set page title, icon, layout |
| 36-173 | CSS & Theming | Dark theme styling (colors, fonts, buttons) |
| 175-195 | Colors & Constants | Define color palette and hardcoded numbers |
| 198-420 | Configuration | Skill name mappings, job categories, CV vocabulary |
| 428-512 | CV Utilities | Functions for skill detection from CV text |
| 544-595 | Data Enrichment | Add job roles and apply links to data |
| 641-860 | Loaders & Helpers | Load CSVs, apply fallbacks, normalize data |
| 865-1348 | Data Processing | Calculate metrics, gaps, similarities, clusters |
| 1455-1805 | `render_global_tab` | Global comparison UI (workbook or upload; no static country charts) |
| 2050-2078 | Chart helpers | `_dark`, `show` — Plotly dark theme |
| 2081-2112 | Data load & nav | `load_a`…`load_d`, `load_global_workbook`, session upload override, sidebar |
| 2133-2421 | Tab 1: UK & Regions | UK Overview + Regional Analysis |
| 2427-2779 | Tab 2: AI Gaps | Gaps, clusters, workshops |
| 2784-2789 | Tab 3: Global | Calls `render_global_tab(...)` |
| 2794+ | Tab 4: CV | CV Evaluator |

---

## Data Loading Pipeline

### The "Step A → B → C → D" Pipeline

The app uses a 4-step data pipeline. Each step builds on the previous one.

```
Raw job listings (UK gaming sample; volume varies with your workbook and pipeline)
  ↓
[STEP A] Clean the raw data
  ✓ Input: step_a_clean_output.csv
  ✓ Contains: company name, job date, skills mentioned
  ✓ One row = one skill mention in one job ad
  ✓ Used by: UK Overview tab, CV Evaluator
  ↓
[STEP B] Cluster skills into categories
  ✓ Input: step_b_clustered_skills (2).csv
  ✓ Contains: Step A data + cluster labels (Game Dev, Soft Skills, etc.)
  ✓ One row = one skill mention with its cluster
  ✓ Used by: AI Gaps tab (cluster stacks)
  ↓
[STEP C] Calculate supply vs demand gaps
  ✓ Input: step_c_gap_scores.csv
  ✓ Contains: Per region, per skill: Demand count, Supply, Gap Score
  ✓ Gap Score = Demand / Supply (higher = more shortage)
  ✓ Used by: AI Gaps tab (heatmaps, bars), CV Evaluator (gap cross-check)
  ↓
[STEP D] Create workshop recommendations
  ✓ Input: step_d_workshop_recommendations.csv
  ✓ Contains: Recommended skills to train per region (ranked by gap)
  ✓ Used by: AI Gaps tab (workshop table), CV Evaluator (skill advice)
  ↓
[GLOBAL] Enhance with worldwide comparison
  ✓ Input: Updated_27_02_26_-_Kabilan.xlsx (raw workbook)
          + city_to_country_tab5 module (maps cities to countries)
  ✓ Creates: Combined_Data_cleaned.xlsx (cleaned & deduplicated)
  ✓ Used by: Global tab (country comparison)
```

### How Data is Loaded (Code Flow)

**In app.py (data load block, ~lines 2081-2091):**

```python
df_a, live_a = load_a()
df_b, live_b = load_b()
df_c, live_c = load_c()
df_d, live_d = load_d()
df_global, global_source_name, global_load_error = load_global_workbook()
# Optional: user-uploaded Combined Data for this session (e.g. Streamlit Cloud)
if st.session_state.get("gc_global_workbook_df") is not None:
    df_global = st.session_state["gc_global_workbook_df"]
    global_source_name = st.session_state.get("gc_global_workbook_name", "Uploaded workbook")
    global_load_error = None
```

**Each Step A–D loader (`load_a`, `load_b`, etc.):**
1. Looks for the CSV in `data/steps/` (or via `_find()`)
2. If found → load with pandas and `@st.cache_data`
3. If NOT found → hardcoded `_fallback_a()` / `_fallback_b()` etc. and `live_* = False`

**Global workbook:** `load_global_workbook()` returns `(DataFrame | None, filename | None, error_message | None)`. It does **not** inject demo country data. The **Global** tab either processes a disk file, an **uploaded** Excel in session state, or shows guidance only (see `render_global_tab`).

**This means:** UK / AI Gaps / CV can still run with Step A–D fallbacks. **Global** needs real Combined Data (on disk or upload) to show live country and skill views.

---

## The Four Main Tabs

### Tab 1: UK & Regions (Lines 2104-2391)

**What you see:**
- Two sub-tabs: "UK Overview" and "Regional Analysis"

#### UK Overview
Shows the big picture of UK gaming job postings:

| Chart/Metric | Shows | Data Source |
|--------------|-------|-------------|
| 4 metrics (top row) | Job ads (workbook), unique skills & rows (Step A), regions | `Updated_...xlsx` `Combined Data` (UK + Gaming Company) for job count; `uk_overview_core_metrics` + Step A for skills |
| Top 15 skills bar chart | Which skills appear most in job postings | Step A (count + %) |
| Skill Demand Over Time | How demand for top skills changed Jul-Oct 2025 | Step A (by month) |

**Code walkthrough:** UK Overview lives under `if tab == "📊 UK & Regions"` → `uk_sub == "UK Overview"` (~lines 2154+). Metrics use `n_jobs` from the workbook count, `n_rows` / `n_skills` / `n_regions` from Step A after filters — not hardcoded constants.

#### Regional Analysis
Shows skill demand by UK region:

| Chart/Metric | Shows | Data Source |
|--------------|-------|-------------|
| 4 mini-tables (top) | Top 5 skills per region (England, Scotland, Wales, N. Ireland) | Step A (filtered by region) |
| Skill demand heatmap (bottom) | 10 top skills × 4 regions, "per 100k" scale | Step A (with population normalization) |

**"Per 100k" means:** Not just "200 jobs mentioned Python", but "200 mentions per 100,000 population in that region". This lets you compare regions fairly (Scotland has fewer people than England, so raw numbers are misleading).

---

### Tab 2: AI Gaps (Lines 2395-2748)

**What you see:**
- Shows which skills the industry needs but can't find

**The story this tab tells:**
```
Demand = "How many jobs want this skill?"
Supply  = "How many job seekers have this skill?"
Gap     = Demand / Supply

HIGH gap = High demand, low supply = OPPORTUNITY/SHORTAGE
LOW gap  = Either balanced, or skill not needed
```

#### Section 1: Pipeline Overview (Lines 2396-2425)
Shows the 4-step pipeline mentioned above.
- 4 metrics showing row count at each step
- This is just informational to explain the process

#### Section 2: Cluster Composition (Lines 2427-2531)
Shows how different skill clusters are distributed by region.

**Clusters are:**
1. Game Dev & Programming
2. Soft Skills (communication, teamwork)
3. Project Management
4. Creative (art, design, animation)
5. Business Tools (Excel, Salesforce, etc.)
6. Cloud & DevOps

**You see:**
- Stacked bar chart: Each region has 6 colored bars (one per cluster)
- Radar chart: Alternative view of same data (6 spokes for clusters, 4 colored lines for regions)

#### Section 3: Gap Heatmap & Workshops (Lines 2536-2668)
Shows supply vs demand by skill.

**Left side:**
- Heatmap: Regions vs Clusters, color = average gap score
- Red (high) = Big shortage
- Blue (low) = Balanced

**Right side:**
- Workshop table from Step D
- Shows which skills to train per region
- Columns: Region, Skill, Cluster, Demand, Supply, Gap, Priority

#### Section 4: Region-Specific Analysis (Lines 2682-2747)
Drill down into one region:

```python
region = st.selectbox("Pick a region:", ["England", "Scotland", ...])
# Shows top 12 skills by gap score for that region
# Bar chart with gap scores
# 4 metrics: top skill, total demand, workshops needed
```

---

### Tab 3: Global (`render_global_tab`, ~1455-1805; invoked from ~2784)

**What you see (when data is available):**
- Country job counts and UK vs world skill analysis from the **Combined Data** sheet

**The data:**
- **Disk:** `load_global_workbook()` uses `_find()` with **`Updated_27_02_26_-_Kabilan.xlsx` first**, then `Combined_Data_cleaned.xlsx` (first file found wins). Sheet: **`Combined Data`**, then `normalize_tab5_dataframe_country`.
- **Upload:** User can upload the same workbook in-session (`gc_global_workbook_upload`); it overrides disk load for that session.
- **If there is no usable workbook and no successful processing:** the tab shows **info / error text and upload** — it does **not** show hardcoded “reference” country rankings or placeholder KPIs.

**Charts (when `use_live` path succeeds):**

| Chart | Shows |
|-------|-------|
| Top countries bar | Gaming job row counts by country (UK highlighted when present) |
| Skill explorer | UK vs world skill shares (when `share_df` is non-empty) |
| Ahead / behind, rankings, similarity | From computed shares when United Kingdom appears in the skill-share matrix |

Skill-level highlights (#1 skill, biggest ahead/behind) come from **data**, not fixed example skill names.

---

### Tab 4: CV Evaluator (Lines 2758-3098)

**What you see:**
- Upload your CV (as text, PDF, or TXT file)
- App extracts skills from your CV
- Shows how your skills match job listings in the UK gaming industry

**The flow:**

```
You → Upload CV
      ↓
App → Detect skills in CV using lexical matching (regex + known aliases)
      ↓
App → Compare against Step A (all skills mentioned in job ads)
      ↓
Show → How many jobs mention your skills
    → How much you overlap with industry
    → Which high-demand skills you're missing
    → Specific job listings you could apply for
    → Gaps in your region
```

#### What it shows:

| Section | Shows |
|---------|-------|
| Metrics (top) | Skills matched, % of jobs reached, priority gaps |
| Left column | Your skills (teal chips), missing high-demand (red chips) |
| Right column | Bar chart of job categories (Engineer, Artist, Designer, etc.) - how well you match each |
| Top 3 jobs | Which roles suit you best (ranked by skill overlap) |
| Matching listings | Table of actual job postings you could apply for (with apply link) |
| Career advice | Suggestions based on your overlap strength |
| Gap cross-check | High-gap skills from Step C/D that you don't have |

**How skill detection works (lines 453-472):**
1. Split your CV text into words
2. Compare against known skill names (from Step A + fallback vocab)
3. Look for aliases ("C++" matches "cpp", "Unreal" matches "unreal engine")
4. Use regex to handle word boundaries (won't match "python" in "micropython")
5. Count matches

---

## Key Helper Functions

### Understanding Common Patterns

These functions appear repeatedly throughout the code:

#### 1. **`_find(*names)`** (Line 641)
Finds a file by name, searching in multiple locations.

```python
file_path = _find("step_a_clean_output.csv")
# Searches in: project root, data/, data/steps/, and recursively everywhere
# Returns: Path object if found, None if not found
```

#### 2. **`cn(skill_name)`** (Line 208)
Normalize skill display names for the UI.

```python
cn("cpp")        # Returns "C++"
cn("ms-office")  # Returns "MS Office"
cn("python")     # Returns "Python" (unchanged)
```

Uses the `_NM` dictionary (lines 198-420) that maps shortened/hyphenated names to display names.

#### 3. **`load_a()`, `load_b()`, `load_c()`, `load_d()`** (Lines 781-829)
Load Step A-D CSV files with caching.

```python
df_a, live_a = load_a()
# df_a = actual data (pandas DataFrame)
# live_a = True if real data, False if fallback demo
```

The `@st.cache_data` decorator (line 780) means: **Don't reload the file every time the page refreshes. Cache it in memory.**

#### 4. **`_dark(fig, h)`** (Line 2027)
Apply dark theme to any Plotly chart.

```python
fig = px.bar(...)       # Create chart with default theme
fig = _dark(fig, h=300) # Apply dark colors & set height to 300px
show(fig, h=300)        # Display in Streamlit
```

Applies colors like `TEAL`, `PURPLE`, `RED` and dark background `#05090F`.

#### 5. **`_cv_detect_skills(text, vocab)`** (Line 453)
Find skill mentions in CV text.

```python
skills_found = _cv_detect_skills(
    cv_text,
    vocabulary=["python", "c++", "unity", ...]
)
# Returns: set of skill tokens found in cv_text
```

Uses regex word boundaries and alias matching (e.g., "C++" → "cpp").

---

## Data Structures & Flow

### Key Data Formats

#### Step A CSV: `step_a_clean_output.csv`
**Represents:** One row per skill mention in a job ad

| Column | Example | Meaning |
|--------|---------|---------|
| Company Category | "AAA Publisher" | Type of gaming company |
| Country | "United Kingdom" | Country |
| State | "England" | UK region |
| Activated Date | "2025-07-15" | When job was posted |
| Skills | "python, communication" | Skills mentioned |
| UK Region | "England" | Normalized region |

**Totals:** 1,121 job ads, ~352 unique skills

#### Step B CSV: `step_b_clustered_skills (2).csv`
**Represents:** Step A + cluster labels

| Additional Column | Example |
|-------------------|---------|
| Cluster | 1 (integer ID) |
| Cluster_Name | "Game Development & Programming" |

**Use:** Group skills into categories for heatmaps and stacked bars

#### Step C CSV: `step_c_gap_scores.csv`
**Represents:** Per-region, per-skill gap analysis

| Column | Example | Meaning |
|--------|---------|---------|
| UK Region | "Scotland" | Region |
| Skills | "python" | Skill name |
| Cluster_Name | "Game Dev & Programming" | Cluster |
| Demand | 45 | # of jobs mentioning this skill |
| Supply | 20.5 | Estimated # of trained individuals (decimal) |
| Gap_Score | 2.19 | Demand / Supply |

**Use:** Show which skills are in shortage (high gap = big shortage)

#### Step D CSV: `step_d_workshop_recommendations.csv`
**Represents:** Recommended training workshops

| Column | Example |
|--------|---------|
| UK_Region | "Wales" |
| Skill | "c#" |
| Demand_Count | 30 |
| Gap_Score | 1.85 |
| Workshop_Recommendation | "HIGH PRIORITY" |
| Cluster_Name | "Game Dev & Programming" |

**Use:** Suggest which skills to train, ranked by priority

#### Global Workbook: `Updated_27_02_26_-_Kabilan.xlsx`
**Represents:** Gaming jobs from 81+ countries

Sheet: `"Combined Data"`

| Column | Example |
|--------|---------|
| Country | "India" |
| City | "Bangalore" |
| Skills | "unity, c#" |
| Company Category | "Mobile Studio" |
| Job Title | "Game Developer" |
| Job Link | "https://..." |
| Activated Date | "2025-09-20" |

**Loading in the app (`load_global_workbook`, ~836+):**
1. Resolve a file path with `_find("Updated_27_02_26_-_Kabilan.xlsx", "Combined_Data_cleaned.xlsx")` (Updated is tried first).
2. Read sheet **`Combined Data`**, then `normalize_tab5_dataframe_country`.
3. Optional offline script `python -m src.preprocess_combined_for_global` can create `Combined_Data_cleaned.xlsx` for a deduped copy; the app will pick it if the raw file is absent.

---

## Supporting Files

### city_to_country_tab5.py

**What it does:** Maps location strings (city names, region names) to canonical country names.

**Example:**
```python
lookup_tab5_location("New York")      # Returns "United States"
lookup_tab5_location("Toronto")       # Returns "Canada"
lookup_tab5_location("London")        # Returns "United Kingdom" (ambiguous city)
```

**Why needed:** The global workbook has entries like:
```
Country="", City="Bangalore"
```
This module normalizes it to:
```
Country="India"
```

**Data:**
- `CITY_TO_COUNTRY`: 700+ city-to-country mappings (hardcoded dictionary)
- `TAB5_KNOWN_COUNTRIES`: List of 81 canonical country names
- `TAB5_CHART_COUNTRIES`: Same but excludes "Remote"

**Main function used in app:**
```python
from src.city_to_country_tab5 import normalize_tab5_dataframe_country

df_global = normalize_tab5_dataframe_country(df_global)
# Fills missing Country column by matching City name
```

---

### preprocess_combined_for_global.py

**What it does:** Clean the raw global workbook before using it in the app.

**Why:** The raw workbook has:
- Duplicate job postings
- Messy city/country data
- Extra whitespace
- Merged skills (multiple skills in one cell)

**What it does step-by-step:**

```
1. Load: Updated_27_02_26_-_Kabilan.xlsx
   ↓
2. Strip: Remove leading/trailing whitespace from all strings
   ↓
3. Normalize: Map city names to countries
   ↓
4. Deduplicate:
   - Create fingerprint ID (by job URL or company+date+title)
   - Group rows with same ID
   - Merge their skills (combine + deduplicate)
   ↓
5. Filter: Keep only rows with non-empty skills
   ↓
6. Output: Combined_Data_cleaned.xlsx
```

**Run it manually:**
```bash
python -m src.preprocess_combined_for_global
# Prints: "Rows in: 5234  out: 4521  removed: 713"
# Creates: data/Combined_Data_cleaned.xlsx
```

**In practice:** If only the raw workbook is present, the app uses that. If both exist, **`Updated_...` is preferred** by `_find` order.

---

## Common Tasks & Where to Find Them

### "I want to..."

#### Add a new skill name mapping
**File:** `app.py`, lines 198-420
**Find:** `_NM = { ... }` dictionary
**Add:** `"your-slug":"Display Name"`

Example:
```python
_NM = {
    "cpp":"C++",
    "python":"Python",
    "your-skill":"Your Skill Name",  # ← Add here
}
```

**Why:** When displaying skills, the app uses `cn(skill_name)` to convert short names to readable names.

---

#### Add a new job category for CV matching
**File:** `app.py`, lines 265-285
**Find:** `CV_JOB_CATS = { ... }` dictionary
**Add:** `"Your Category": ["skill1", "skill2", ...]`

Example:
```python
CV_JOB_CATS = {
    "Game Programmer": ["python", "c++", "unity", ...],
    "Your New Role": ["skill1", "skill2"],  # ← Add here
}
```

**Why:** The CV Evaluator scores your CV against these 9 job categories. Adding new ones makes it score more role types.

---

#### Change the dark theme colors
**File:** `app.py`, lines 175-186
**Find:** Color constants

Example:
```python
TEAL   = "#00E5CC"  # Primary highlight
PURPLE = "#A78BFA"  # Accent color
RED    = "#FF5572"  # Error/shortage
# ... change hex codes above
```

**Also:** Update the CSS section (lines 36-173) if you want to change background, text, or border colors.

---

#### Add a new chart to Tab 1 (UK & Regions)
**File:** `app.py`, starting at line 2104
**Structure:**
```python
# Inside Tab 1 section:
if tab == "📊 UK & Regions":
    sub_tab = st.radio("Pick view:", ["UK Overview", "Regional Analysis"])
    
    if sub_tab == "UK Overview":
        # Display metrics, charts for UK-wide view
        # Your new chart goes here
    
    else:  # "Regional Analysis"
        # Display region-specific charts
        # Or your new chart here
```

**Pattern:**
```python
# Load data
df_a, live_a = load_a()

# Process data
top_skills = df_a['Skills'].value_counts().head(10)

# Create chart
fig = px.bar(top_skills, title="Top 10 Skills")
fig = _dark(fig, h=400)

# Display
show(fig, h=400)
```

---

#### Modify the CV skill detection (regex patterns)
**File:** `app.py`, lines 453-472
**Function:** `_cv_detect_skills(text, vocab)`

Current logic:
1. Split text into words
2. Match against vocab + aliases
3. Use regex with word boundaries

To add new aliases:
```python
CV_SKILL_ALIASES = {
    "unreal": ["unreal engine", "ue4", "ue5"],
    "c plus plus": ["c++", "cpp"],
    "your-skill": ["alias1", "alias2"],  # ← Add here
}
```

---

#### Add a new region to the analysis
**File:** `app.py`, line 188-191
**Find:** `POP = {...}` dictionary

Current:
```python
POP = {
    "England": 56_490_048,
    "Scotland": 5_490_000,
    "Wales": 3_200_000,
    "Northern Ireland": 1_910_000,
}
```

Add:
```python
POP = {
    "England": 56_490_048,
    "Scotland": 5_490_000,
    "Wales": 3_200_000,
    "Northern Ireland": 1_910_000,
    "Your Region": 1_000_000,  # ← Add with population
}
```

**Then:** Make sure Step A/B/C CSVs have this region in their "UK Region" column.

---

#### Change what metrics appear in Tab 2 (AI Gaps)
**File:** `app.py`, lines 2682-2747
**Find:** The region dropdown section

Current shows:
- Top skill by gap
- Total demand
- # of workshops
- # of clusters

Modify the `st.metric()` calls to show different values.

---

#### Add filtering to Tab 4 (CV Evaluator)
**File:** `app.py`, lines 2758-3098
**Current filters:**
- Region (for cross-checking gaps)

To add a skill filter (e.g., "show only jobs mentioning Python"):
```python
selected_skills = st.multiselect("Filter by skills:", df_a['Skills'].unique())
matching_jobs = df_jobs[df_jobs['Skills'].str.contains('|'.join(selected_skills))]
# Display filtered matching_jobs table
```

---

## Summary: The Journey of Data

**From start to finish:**

```
1. User opens app
   → streamlit run app.py

2. App loads data
   → load_a(), load_b(), load_c(), load_d(), load_global_workbook()
   → Each cached in memory

3. User sees sidebar
   → 4-option radio button
   → Choices: UK & Regions | AI Gaps | Global | CV Evaluator

4. User clicks "UK & Regions"
   → Tab 1 renders
   → Loads Step A data
   → Calculates top 15 skills, regional summaries
   → Displays metrics, charts, tables

5. User clicks "AI Gaps"
   → Tab 2 renders
   → Loads Step B, C, D data
   → Calculates clusters, gaps, heatmaps
   → Displays cluster composition, gap analysis, workshops

6. User clicks "Global"
   → Renders `render_global_tab` (or shows upload prompt if no data)
   → Workbook from disk and/or user upload; session state can override
   → Normalizes countries using `city_to_country_tab5`
   → When possible: skill shares, rankings, similarity from real rows only

7. User clicks "CV Evaluator"
   → Tab 4 renders
   → User uploads CV (text/PDF/TXT)
   → App detects skills using lexical matching
   → Filters Step A for matching jobs
   → Displays overlap, missing skills, recommendations

8. User closes browser
   → Session ends
   → Data cached in memory is freed
```

---

## Next Steps

Now that you understand the codebase:

- **Run it:** `streamlit run app.py`
- **Explore the code:** Open `app.py` in your editor and follow the line numbers in this guide
- **Modify:** Use "Common Tasks & Where to Find Them" to make changes
- **Debug:** Add print statements or use Python debugger to understand data flow
- **Deploy:** Push to GitHub and set up Streamlit Cloud

---

**Questions? Check the code comments.** Each section in `app.py` has a comment header explaining what it does.

Happy coding! 🎮
