# GC Dashboard (Streamlit)

Hosted Streamlit dashboard for the **UK Gaming Industry — Skill Demand Analysis**.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Data & assets expected

- CSV inputs:
  - `data/steps/step_a_clean_output.csv`
  - `data/steps/step_b_clustered_skills (2).csv`
  - `data/steps/step_c_gap_scores.csv`
  - `data/steps/step_d_workshop_recommendations.csv`
  - `data/universal_skills.csv`
- Chart images: stored in `assets/expr_charts/` and `assets/stage3_charts/`.
- Global comparison (sidebar **Global**):
  - Put `Updated_27_02_26_-_Kabilan.xlsx` (sheet: `Combined Data`) in `data/` or project root (auto-discovered), **or**
  - On Streamlit Cloud without committing the file: set **`GLOBAL_COMBINED_WORKBOOK_URL`** in app secrets (HTTPS URL to the `.xlsx`), **or**
  - Upload once per browser session via the Global tab expander.

## Deploy (Streamlit Community Cloud)

1. Create a GitHub repo and push this folder (include the CSVs and image assets you want visible in the hosted app).
2. In Streamlit Community Cloud, create a new app:
   - **Repository**: your GitHub repo
   - **Branch**: `main`
   - **Main file path**: `app.py`

