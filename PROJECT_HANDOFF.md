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

Optional: build a cleaned global dataset from the raw workbook (writes `Combined_Data_cleaned.xlsx`, gitignored):

```bash
python preprocess_combined_for_global.py
```

Requires `Updated_27_02_26_-_Kabilan.xlsx` at project root with sheet **`Combined Data`**.

## Repository layout (important files)

| Path | Role |
|------|------|
| `app.py` | Main Streamlit app (~2k lines): tabs, loaders, all Plotly figures |
| `city_to_country_tab5.py` | City → country mapping and normalization for global tab (`TAB5_CHART_COUNTRIES`, `normalize_tab5_dataframe_country`) |
| `preprocess_combined_for_global.py` | Dedupes/merges raw `Combined Data` → `Combined_Data_cleaned.xlsx` |
| `Step files/step_a_clean_output.csv` | Step A — UK overview metrics |
| `Step files/step_b_clustered_skills (2).csv` | Step B — clustered skills (note: filename has space and `(2)`) |
| `Step files/step_c_gap_scores.csv` | Step C — AI gap scores |
| `Step files/step_d_workshop_recommendations.csv` | Step D — workshop recommendations |
| `universal_skills.csv` | Listed in README; **not imported in `app.py`** (legacy/extra asset) |
| `Updated_27_02_26_-_Kabilan.xlsx` | Raw global comparison workbook (sheet `Combined Data`) — may be absent in git |
| `Combined_Data_cleaned.xlsx` | Preferred input for global tab when present (generated; in `.gitignore`) |
| `gaming_dashboard.html` | Standalone HTML demo/visual; **not wired into Streamlit** unless you integrate it |
| `.streamlit/config.toml` | Streamlit theme (e.g. dark) |
| `.gitignore` | Ignores `Combined_Data_cleaned.xlsx`, secrets, `__pycache__` |
| `.devcontainer/devcontainer.json` | Optional VS Code dev container |
| `README.md` | Short run/deploy instructions |

## `app.py` — behavior summary

- **Navigation:** Sidebar `st.radio` — `NAV_OPTIONS` (must stay in sync if you rename sections):
  - `📊 UK & Regions` — UK Overview / Regional Analysis; metric definitions expander; regional hero tiles use the same “top skill /100k” rule; heatmap warns when using static fallback.
  - `🤖 AI Gaps` — pipeline, cluster stack, heatmaps, Step D table, per-region bars; suggested reading order; Step D validated against required columns; sparse-region caption for low Step C row counts.
  - `🌍 Global` — live workbook drives country bars and ahead/behind; ranking table + cosine similarity computed from data when possible; static blocks labelled as reference when no workbook.
  - `📄 CV` — lexical/alias matching only; region picker links high-gap Step C / Step D skills not matched on the CV.
- **Data loading:** `load_a()` … `load_d()` plus `_find()` for CSVs under `Step files/` (or repo root). Global: `load_global_workbook()` prefers **`Combined_Data_cleaned.xlsx`**, else **`Updated_27_02_26_-_Kabilan.xlsx`** (sheet **`Combined Data`**).
- **Step D contract:** Live workshop table requires columns `UK_Region`, `Skill`, `Demand_Count`, `Gap_Score` (optional `Workshop_Recommendation`). See `step_d_workshop_recommendations.csv`.
- **Imports from `city_to_country_tab5`:** `normalize_tab5_dataframe_country` for the global workbook path.
- **Styling:** Plotly `template="plotly_dark"` (and custom layout) for consistency.
- **Docstring** states: all charts from CSV/Excel only, no static chart images in-app.

## Global comparison (sidebar: “🌍 Global”)

- Prefers **`Combined_Data_cleaned.xlsx`** when found anywhere under the app directory tree.
- Falls back to **`Updated_27_02_26_-_Kabilan.xlsx`** (sheet **`Combined Data`**).
- UI may mention running `preprocess_combined_for_global.py` when using the raw workbook.

## `preprocess_combined_for_global.py`

- **Reads:** `Updated_27_02_26_-_Kabilan.xlsx`, sheet `"Combined Data"`.
- **Writes:** `Combined_Data_cleaned.xlsx` at project root.
- Uses `normalize_tab5_dataframe_country` from `city_to_country_tab5.py` for country cleanup.

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
