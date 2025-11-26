# src/ab_experiment/data_access.py

from pathlib import Path
import pandas as pd


def get_experiment_df() -> pd.DataFrame:
    """
    Load the marketing_AB.csv file and return a cleaned DataFrame.

    This assumes your repo structure is:

        MARKETING-AB-EXPERIMENT/
          data_raw/
            marketing_AB.csv
          src/
            ab_experiment/
              data_access.py
              __init__.py
          notebooks/
            ...

    """
    # 1. Find the project root: go two folders up from THIS file:
    #    data_access.py -> ab_experiment -> src -> PROJECT_ROOT
    project_root = Path(__file__).resolve().parents[2]

    # 2. Build the path to data_raw/marketing_AB.csv
    csv_path = project_root / "data_raw" / "marketing_AB.csv"

    # 3. Read the CSV
    raw = pd.read_csv(csv_path)

    # 4. Apply the same cleaning you used in your notebook
    df = raw.copy()
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(" ", "_")
          .str.replace("/", "_")
    )

    df["user_id"] = df["user_id"].astype("int64")

    df["converted"] = df["converted"].map(
        {True: 1, False: 0, "True": 1, "False": 0, 1: 1, 0: 0}
    ).astype("int64")

    df["total_ads"] = df["total_ads"].astype("int64")
    df["most_ads_hour"] = df["most_ads_hour"].astype("int64")

    return df
