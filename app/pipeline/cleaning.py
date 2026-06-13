# Data cleaning rules for raw transaction CSVs (assignment step a)
import re
import pandas as pd


def normalize_date(value: str) -> str:
    """Convert known date formats to ISO 8601 (YYYY-MM-DD)."""
    value = str(value).strip()

    # Format: YYYY/MM/DD  (e.g. 2024/02/05)
    if re.match(r"^\d{4}/\d{2}/\d{2}$", value):
        year, month, day = value.split("/")
        return f"{year}-{month}-{day}"

    # Format: DD-MM-YYYY  (e.g. 04-09-2024)
    if re.match(r"^\d{2}-\d{2}-\d{4}$", value):
        day, month, year = value.split("-")
        return f"{year}-{month}-{day}"

    # Unrecognized format - leave as-is rather than guessing
    return value


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all cleaning rules from assignment step (a)."""
    df = df.copy()

    # Normalize dates to ISO 8601
    df["date"] = df["date"].apply(normalize_date)

    # Strip "$" from amounts and convert to numeric
    df["amount"] = (
        df["amount"].astype(str).str.replace("$", "", regex=False).astype(float)
    )

    # Uppercase currency values (inr -> INR)
    df["currency"] = df["currency"].str.upper()

    # Uppercase status values (success -> SUCCESS)
    df["status"] = df["status"].str.upper()

    # Fill missing categories
    df["category"] = df["category"].fillna("Uncategorised")

    # Remove exact duplicate rows (checked after normalization,
    # so rows that only differed by casing are now correctly seen as duplicates)
    df = df.drop_duplicates()

    return df