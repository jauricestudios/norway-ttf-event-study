from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "ttf"
    / "ice_dutch_ttf_futures_2024-07-01_to_2026-09-17.csv"
)

df = pd.read_csv(SOURCE_FILE)

print(f"Source: {SOURCE_FILE}")
print(f"Rows: {len(df):,}")
print(f"Columns: {list(df.columns)}")
print(df.head())
# Validate raw source structure

EXPECTED_COLUMNS = [
    "Date",
    "Price",
    "Open",
    "High",
    "Low",
    "Vol.",
    "Change %",
]

if list(df.columns) != EXPECTED_COLUMNS:
    raise ValueError(
        f"Unexpected columns.\n"
        f"Expected: {EXPECTED_COLUMNS}\n"
        f"Received: {list(df.columns)}"
    )

if df.empty:
    raise ValueError("Source file contains no observations.")

print("Raw structure validation: PASS")
print("Raw structure validation: PASS")
# Validate dates

parsed_dates = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

invalid_dates = parsed_dates.isna().sum()

if invalid_dates > 0:
    raise ValueError(
        f"Date validation failed: {invalid_dates} dates could not be parsed."
    )

print("Date parsing validation: PASS")
print(f"Date range: {parsed_dates.min().date()} to {parsed_dates.max().date()}")
# Validate daily grain

duplicate_dates = parsed_dates.duplicated().sum()

if duplicate_dates > 0:
    duplicate_rows = df.loc[
        parsed_dates.duplicated(keep=False),
        ["Date", "Price", "Open", "High", "Low"]
    ]

    raise ValueError(
        f"Daily grain validation failed: {duplicate_dates} duplicate dates found.\n"
        f"{duplicate_rows.to_string(index=False)}"
    )

print("Daily grain validation: PASS")
print(f"Unique trading dates: {parsed_dates.nunique()}")
# Validate missingness

missing_counts = df[EXPECTED_COLUMNS].isna().sum()

print("\nMissing values:")
print(missing_counts)

if missing_counts.sum() > 0:
    raise ValueError(
        "Missing-value validation failed.\n"
        f"{missing_counts[missing_counts > 0]}"
    )

print("Missingness validation: PASS")
