# -*- coding: utf-8 -*-
"""
Build a deduplicated, cleaned Combined Data extract for Tab 5 / global comparison.

Reads: Updated_27_02_26_-_Kabilan.xlsx (sheet "Combined Data")
Writes: Combined_Data_cleaned.xlsx (same columns; one row per job; merged skills)

Run from project root:
    python preprocess_combined_for_global.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from city_to_country_tab5 import CITY_TO_COUNTRY, CITY_TO_COUNTRY_SUPPLEMENT

APP_DIR = Path(__file__).resolve().parent
SOURCE_XLSX = APP_DIR / "Updated_27_02_26_-_Kabilan.xlsx"
OUT_XLSX = APP_DIR / "Combined_Data_cleaned.xlsx"
SHEET = "Combined Data"


def _strip_all_strings(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        if out[c].dtype == object or str(out[c].dtype) == "string":
            out[c] = out[c].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return out


def _normalize_job_link(val: object) -> str:
    if pd.isna(val):
        return ""
    s = str(val).strip().lower()
    if s in ("", "nan", "none", "null"):
        return ""
    s = s.split("?")[0].split("#")[0].rstrip("/")
    return s


def _is_nullish(val: object) -> bool:
    if pd.isna(val):
        return True
    s = str(val).strip().lower()
    return s in ("", "nan", "none", "null", "n/a", "#n/a")


def _merge_skills_series(ser: pd.Series) -> str:
    seen: list[str] = []
    bag: set[str] = set()
    for raw in ser.dropna():
        for part in str(raw).split(","):
            x = part.strip().lower()
            if not x or x in ("nan", "none", "null"):
                continue
            if x == "game-texts":
                continue
            if x not in bag:
                bag.add(x)
                seen.append(x)
    return ", ".join(seen)


def _job_key_column(df: pd.DataFrame) -> pd.Series:
    norm_link = df["Job Link"].map(_normalize_job_link) if "Job Link" in df.columns else pd.Series("", index=df.index)
    fp_cols = [c for c in ("Company", "Title", "Activated Date", "Country", "City", "Company Category") if c in df.columns]
    if fp_cols:
        sub = df[fp_cols].fillna("").astype(str).apply(lambda x: x.str.strip().str.lower())
        sub = sub.replace({"nan": "", "none": "", "null": ""})
        fp_raw = sub.agg("|".join, axis=1)
        fp = "fp:" + fp_raw.map(lambda x: hashlib.md5(x.encode("utf-8", errors="replace")).hexdigest())
    else:
        fp = "fp:" + pd.RangeIndex(len(df)).astype(str)
    has_url = norm_link != ""
    return np.where(has_url, "url:" + norm_link.to_numpy(dtype=object), fp.to_numpy(dtype=object))


def _normalize_countries(df: pd.DataFrame, city_map_ci: dict[str, str]) -> pd.DataFrame:
    out = df.copy()
    if "Country" not in out.columns:
        return out

    def one_country(row: pd.Series) -> str:
        c = row.get("Country")
        if not _is_nullish(c):
            s = str(c).strip()
            mapped = city_map_ci.get(s.lower(), s)
        else:
            mapped = ""
        if _is_nullish(mapped) or mapped == "":
            cy = row.get("City")
            if not _is_nullish(cy):
                mapped = city_map_ci.get(str(cy).strip().lower(), str(cy).strip())
        if _is_nullish(mapped):
            return ""
        s2 = str(mapped).strip()
        if s2 in ("US", "USA", "U.S.A", "U.S.", "United States of America"):
            return "United States"
        if s2 in ("UK", "Britain", "Great Britain", "England", "Scotland", "Wales", "Northern Ireland"):
            return "United Kingdom"
        return s2

    out["Country"] = out.apply(one_country, axis=1)
    return out


def preprocess() -> pd.DataFrame:
    if not SOURCE_XLSX.exists():
        raise FileNotFoundError(f"Missing source workbook: {SOURCE_XLSX}")

    df = pd.read_excel(SOURCE_XLSX, sheet_name=SHEET, engine="openpyxl")
    original_cols = list(df.columns)
    n_in = len(df)

    df = df.dropna(axis=1, how="all")
    df = _strip_all_strings(df)

    city_map = {**CITY_TO_COUNTRY_SUPPLEMENT, **CITY_TO_COUNTRY}
    city_map_ci = {str(k).strip().lower(): v for k, v in city_map.items()}

    df = _normalize_countries(df, city_map_ci)

    df["_job_key"] = _job_key_column(df)

    skills_merged = df.groupby("_job_key", sort=False)["Skills"].apply(_merge_skills_series)
    dedup = df.drop_duplicates(subset=["_job_key"], keep="first").copy()
    dedup["Skills"] = dedup["_job_key"].map(skills_merged)
    dedup = dedup.drop(columns=["_job_key"])

    dedup = dedup.loc[~dedup["Skills"].astype(str).str.strip().eq("")].copy()

    for c in original_cols:
        if c not in dedup.columns:
            dedup[c] = np.nan
    dedup = dedup[[c for c in original_cols if c in dedup.columns]]

    if "Activated Date" in dedup.columns:
        d = pd.to_datetime(dedup["Activated Date"], errors="coerce")
        dedup = dedup.assign(_d=d).sort_values("_d", ascending=False).drop(columns=["_d"])

    dedup = dedup.reset_index(drop=True)
    print(f"Rows in: {n_in:,}  out: {len(dedup):,}  removed: {n_in - len(dedup):,}")
    g = (dedup["Company Category"].astype(str).str.strip() == "Gaming Company").sum()
    print(f"Gaming Company rows (cleaned): {g:,}")
    return dedup


def main() -> None:
    clean = preprocess()
    clean.to_excel(OUT_XLSX, sheet_name=SHEET, index=False, engine="openpyxl")
    print(f"Wrote {OUT_XLSX}")


if __name__ == "__main__":
    main()
