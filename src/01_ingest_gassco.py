from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path.cwd()

files = {
    2024: ROOT / "data/raw/gassco/gassco_umm_unplanned_2024.xlsx",
    2025: ROOT / "data/raw/gassco/gassco_umm_unplanned_2025.xlsx",
    2026: ROOT / "data/raw/gassco/gassco_umm_unplanned_2026.xlsx",
}

columns = [
    "message_id",
    "asset",
    "event_status",
    "unavailability_type",
    "event_type",
    "publication_time",
    "event_start",
    "event_stop",
    "unit",
    "technical_capacity",
    "available_capacity",
    "unavailable_capacity",
    "reason",
    "remarks",
    "balancing_zone",
    "market_participant",
    "market_participant_code",
    "asset_eic_code",
]

frames = []

for year, path in files.items():

    df = pd.read_excel(
        path,
        sheet_name="Past Events",
        header=None,
        skiprows=3
    )

    df = df.iloc[:, :18]
    df.columns = columns

    df["source_year"] = year
    df["source_file"] = path.name
    df["source_excel_row"] = np.arange(4, 4 + len(df))

    frames.append(df)

gassco = pd.concat(frames, ignore_index=True)

gassco = gassco.dropna(
    how="all",
    subset=columns
)

text_cols = [
    "message_id",
    "asset",
    "event_status",
    "unavailability_type",
    "event_type",
    "unit",
    "reason",
    "remarks",
    "balancing_zone",
    "market_participant",
    "market_participant_code",
    "asset_eic_code",
]

for col in text_cols:
    gassco[col] = (
        gassco[col]
        .astype("string")
        .str.strip()
    )

for col in [
    "publication_time",
    "event_start",
    "event_stop"
]:
    gassco[col] = pd.to_datetime(
        gassco[col],
        errors="coerce"
    )

for col in [
    "technical_capacity",
    "available_capacity",
    "unavailable_capacity"
]:
    gassco[col] = pd.to_numeric(
        gassco[col],
        errors="coerce"
    )

print("Rows:", len(gassco))
print("Unique message IDs:", gassco["message_id"].nunique())
print(gassco["source_year"].value_counts().sort_index())

out = ROOT / "data/staging/gassco_umm_import.csv"
out.parent.mkdir(parents=True, exist_ok=True)

gassco.to_csv(
    out,
    index=False,
    date_format="%Y-%m-%d %H:%M:%S"
)

print(f"Saved: {out}")
