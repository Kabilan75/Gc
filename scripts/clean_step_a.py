import pandas as pd
from pathlib import Path


def main() -> None:
    src = Path("data/steps/step_a_clean_output.csv")
    backup_dir = Path("archive")
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / "step_a_clean_output_raw.csv"

    df = pd.read_csv(src)
    skills = df["Skills"].astype(str).str.strip()
    region = df["UK Region"].astype(str).str.strip()

    raw_rows = len(df)
    removed_game_texts = int((skills == "game-texts").sum())
    removed_unknown_region = int((region == "Unknown").sum())

    kept = df[(skills != "game-texts") & (region != "Unknown")].copy()

    # Backup the original file before overwriting.
    backup.write_bytes(src.read_bytes())
    kept.to_csv(src, index=False)

    print("raw_rows", raw_rows)
    print("removed_game_texts", removed_game_texts)
    print("removed_unknown_region", removed_unknown_region)
    print("kept_rows", len(kept))


if __name__ == "__main__":
    main()

