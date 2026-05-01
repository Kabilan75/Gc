from __future__ import annotations

from pathlib import Path

import pandas as pd


def _pick_source() -> Path:
    # Keep consistent with app.py: prefers Combined_Data_cleaned.xlsx then Updated_27_02_26_-_Kabilan.xlsx
    for p in (Path("Combined_Data_cleaned.xlsx"), Path("data/Updated_27_02_26_-_Kabilan.xlsx")):
        if p.exists():
            return p
    raise FileNotFoundError("No global workbook found.")


def _dedupe_key(df: pd.DataFrame) -> list[str]:
    # Best-case: a stable URL/link.
    if "Job Link" in df.columns:
        return ["Job Link"]

    # Fallback: composite key; works when link missing but metadata is stable.
    candidates = [
        "Title",
        "Company",
        "Company Name",
        "Location",
        "City",
        "State",
        "Country",
        "Activated Date",
        "Posting Date",
    ]
    return [c for c in candidates if c in df.columns]


def main() -> None:
    src = _pick_source()
    sheet = "Combined Data"

    archive_dir = Path("archive")
    archive_dir.mkdir(parents=True, exist_ok=True)

    backup = archive_dir / f"{src.stem}_raw{src.suffix}"
    out = archive_dir / f"{src.stem}_deduped{src.suffix}"

    # Read
    df = pd.read_excel(src, sheet_name=sheet, engine="openpyxl")

    # Basic cleaning consistent with app intent
    if "Company Category" in df.columns:
        df = df[df["Company Category"].astype(str).str.strip() == "Gaming Company"].copy()
    if "Country" in df.columns:
        df["Country"] = df["Country"].astype(str).str.strip()

    before_total = int(len(df))
    before_uk = int((df.get("Country", "") == "United Kingdom").sum()) if "Country" in df.columns else 0

    key_cols = _dedupe_key(df)
    if not key_cols:
        raise ValueError("No usable dedupe key columns found (no Job Link and no fallback metadata columns).")

    # Normalize key columns (strip + lower for string columns)
    norm = df.copy()
    for c in key_cols:
        if c in norm.columns:
            norm[c] = norm[c].astype(str).str.strip()
            # Links/titles/companies are case-insensitive for dedupe purposes
            norm[c] = norm[c].str.lower()

    deduped = df.loc[norm.drop_duplicates(subset=key_cols).index].copy()

    after_total = int(len(deduped))
    after_uk = int((deduped.get("Country", "") == "United Kingdom").sum()) if "Country" in deduped.columns else 0

    # Backup original + write output (non-destructive: doesn't overwrite src)
    if not backup.exists():
        backup.write_bytes(src.read_bytes())

    with pd.ExcelWriter(out, engine="openpyxl") as w:
        deduped.to_excel(w, sheet_name=sheet, index=False)

    print("source", str(src))
    print("sheet", sheet)
    print("dedupe_key_cols", ",".join(key_cols))
    print("before_total_jobs", before_total)
    print("before_uk_jobs", before_uk)
    print("after_total_jobs", after_total)
    print("after_uk_jobs", after_uk)
    print("wrote_deduped", str(out))
    print("backup_original", str(backup))


if __name__ == "__main__":
    main()

