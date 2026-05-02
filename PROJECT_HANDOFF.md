# Project handoff — GC Dashboard (UK Gaming Skill Demand)

Use this document to continue development without browsing the repo. Paths are relative to the project root.

## What it is

A **Streamlit** dashboard for **UK Gaming Industry — Skill Demand Analysis**. Charts are **Plotly** only (dark theme); data comes from **CSV** and **Excel** files on disk (or uploaded for the global workbook).

## Stack (see `requirements.txt`)

| Package    | Purpose                          |
|-----------|-----------------------------------|
| streamlit | Web UI                            |
| pandas    | Data loading / transforms         |
| plotly    | Interactive charts              |
| openpyxl  | Read/write `.xlsx`              |
| numpy     | Numerics where needed            |
| xlrd      | Legacy `.xls` if ever required   |

Minimum versions are pinned as `>=` in `requirements.txt` (e.g. streamlit>=1.28.0).

## How to run

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Optional: build a cleaned global dataset from the raw workbook (writes `Combined_Data_cleaned.xlsx` to `data/`, gitignored):

```bash
python -m src.preprocess_combined_for_global
```

Requires `data/Updated_27_02_26_-_Kabilan.xlsx` with sheet **`Combined Data`**.

## Repository layout (important files)

| Path | Role |
|------|------|
| `app.py` | Main Streamlit app (~3.1k lines): tabs, loaders, all Plotly figures |
| `src/city_to_country_tab5.py` | City → country mapping and normalization for global tab (`TAB5_CHART_COUNTRIES`, `normalize_tab5_dataframe_country`) |
| `src/preprocess_combined_for_global.py` | Dedupes/merges raw `Combined Data` → `Combined_Data_cleaned.xlsx` |
| `data/steps/step_a_clean_output.csv` | Step A — UK overview metrics |
| `data/steps/step_b_clustered_skills (2).csv` | Step B — clustered skills (note: filename has space and `(2)`) |
| `data/steps/step_c_gap_scores.csv` | Step C — AI gap scores |
| `data/steps/step_d_workshop_recommendations.csv` | Step D — workshop recommendations |
| `data/universal_skills.csv` | Not imported in `app.py`; available for future use |
| `data/Updated_27_02_26_-_Kabilan.xlsx` | Raw global comparison workbook (sheet `Combined Data`) — may be absent in git |
| `data/Combined_Data_cleaned.xlsx` | Optional deduped output from preprocess; used only if the raw `Updated_...` file is missing (`_find` tries raw first) |
| `assets/gaming_dashboard.html` | Standalone HTML demo/visual; **not wired into Streamlit** unless you integrate it |
| `.streamlit/config.toml` | Streamlit theme (e.g. dark) |
| `.gitignore` | Ignores `data/Combined_Data_cleaned.xlsx`, secrets, `__pycache__` |
| `.devcontainer/devcontainer.json` | Optional VS Code dev container |
| `README.md` | Short run/deploy instructions |

## `app.py` — behavior summary

- **Navigation:** Sidebar `st.radio` — `NAV_OPTIONS` (must stay in sync if you rename sections):
  - `📊 UK & Regions` — UK Overview / Regional Analysis; metric definitions expander; regional hero tiles use the same “top skill /100k” rule; heatmap warns when using static fallback.
  - `🤖 AI Gaps` — pipeline, cluster stack, heatmaps, Step D table, per-region bars; suggested reading order; Step D validated against required columns; sparse-region caption for low Step C row counts.
  - `🌍 Global` — country bars and skill views only from **Combined Data** (disk or **session upload**). No hardcoded reference charts; without data, the tab explains upload / missing file.
  - `📄 CV` — lexical/alias matching only; region picker links high-gap Step C / Step D skills not matched on the CV.
- **Data loading:** `load_a()` … `load_d()` plus `_find()` for CSVs under `data/steps/` (or repo root). Global: `load_global_workbook()` returns `(df, name, error)` and resolves **`Updated_27_02_26_-_Kabilan.xlsx`** before **`Combined_Data_cleaned.xlsx`**. After load, **`gc_global_workbook_df`** in session state (user upload) replaces disk data for that session.
- **Step D contract:** Live workshop table requires columns `UK_Region`, `Skill`, `Demand_Count`, `Gap_Score` (optional `Workshop_Recommendation`). See `step_d_workshop_recommendations.csv`.
- **Imports from `city_to_country_tab5`:** `normalize_tab5_dataframe_country` for the global workbook path.
- **Styling:** Plotly `template="plotly_dark"` (and custom layout) for consistency.
- **Docstring** states: all charts from CSV/Excel only, no static chart images in-app.

## Global comparison (sidebar: “🌍 Global”)

- **`load_global_workbook()`** uses `_find("Updated_27_02_26_-_Kabilan.xlsx", "Combined_Data_cleaned.xlsx")` — **raw workbook first** when both exist.
- Sheet **`Combined Data`**; optional **`python -m src.preprocess_combined_for_global`** builds the cleaned file for offline dedupe.
- **Streamlit Cloud:** if the repo has no Excel, users **upload** the workbook in the Global tab (`gc_global_workbook_*` session keys).

## `src/preprocess_combined_for_global.py`

- **Reads:** `data/Updated_27_02_26_-_Kabilan.xlsx`, sheet `"Combined Data"`.
- **Writes:** `data/Combined_Data_cleaned.xlsx`.
- Uses `normalize_tab5_dataframe_country` from `src/city_to_country_tab5.py` for country cleanup.

## Deploy (Streamlit Community Cloud)

- Main file: **`app.py`**
- Push repo with CSVs (and optional Excel) as needed; large or private data may require secrets or external storage.

## Notes for future maintainers / LLMs

1. **Step B filename:** Code may reference `step_b_clustered_skills (2).csv` or a fallback without `(2)` — confirm `load_step_b()` in `app.py` if files are renamed.
2. **`universal_skills.csv`:** Safe to use for new features; currently unused by the app.
3. **`gaming_dashboard.html`:** Separate artifact; embedding would require `st.components` or an iframe + hosting considerations.
4. **Secrets:** `.streamlit/secrets.toml` is gitignored; use for API keys if you add non-file data sources later.

---

*Generated for handoff to another model or developer. Update this file when architecture or data contracts change.*
