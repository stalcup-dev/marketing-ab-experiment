import pandas as pd

# Load + standardize marketing A/B test data
RENAME_MAP = {
    "test group": "test_group",
    "converted": "converted",
    "total ads": "total_ads",
    "most ads day": "most_ads_day",
    "most ads hour": "most_ads_hour",
    "user id": "user_id",
    "user_id": "user_id",
}

def load_marketing_ab(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Normalize columns (lowercase + strip whitespace)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={k.lower(): v for k, v in RENAME_MAP.items()})

    # Ensure required fields exist
    required = {"test_group", "converted"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Found: {list(df.columns)}")

    # Enforce types
    df["test_group"] = df["test_group"].astype(str).str.lower()
    df["converted"]  = df["converted"].astype(int)

    return df
