from dataclasses import dataclass
from typing import Dict, Optional
import pandas as pd
from scipy.stats import chisquare

#------SRM (Sample Ratio Mismatch)------ check for A/B test traffic allocation
# Detects whether actual user counts per variant deviate significantly from expected split
# Uses Chi-square goodness-of-fit test
# Container for SRM results (clean and typed return object)
@dataclass
class SRMResult:
    observed: Dict[str, int]     # Actual observed counts per variant/group
    expected: Dict[str, float]   # Expected counts based on target traffic split
    chi2: float                  # Chi-square statistic
    p_value: float               # Probability of observing deviation this large under null
    pass_srm: bool               # True = no traffic imbalance detected (no SRM flag)

def srm_check(
    df: pd.DataFrame,
    group_col: str = "test_group",               # Column that contains variant labels
    expected_split: Optional[Dict[str, float]] = None,  # {'A':0.5, 'B':0.5} style expected ratio
    alpha: float = 0.01,                          # Significance threshold (strict for SRM)
) -> SRMResult:

    # Count number of users per group from dataset
    counts = df[group_col].value_counts().to_dict()

    # Sort group names to ensure pairing stays consistent for obs vs exp arrays
    groups = sorted(counts.keys())
    total = sum(counts.values())

    # If caller doesn't supply expected allocation, assume equal traffic split
    # e.g. for A/B test -> 50/50; for A/B/C -> 33/33/33 etc.
    if expected_split is None:
        expected_split = {g: 1.0 / len(groups) for g in groups}

    # Convert expected % allocation -> expected user counts
    expected_counts = {g: expected_split[g] * total for g in groups}

    # Construct aligned lists for chi-square calculation
    # obs = raw counts, exp = mathematically expected counts
    obs = [counts[g] for g in groups]
    exp = [expected_counts[g] for g in groups]

    # Chi-square test → checks whether observed allocation differs from expectation
    chi2, p = chisquare(f_obs=obs, f_exp=exp)

    # Package results into structured dataclass
    return SRMResult(
        observed=counts,
        expected=expected_counts,
        chi2=float(chi2),
        p_value=float(p),
        pass_srm=(p >= alpha)   # If p-value is too small, traffic imbalance likely (SRM detected)
    )

#If p < 0.01 → fail SRM (raise a big red flag in the report).

# -----Categorical balance check using Chi-square test-----
# Evaluates whether categorical variable distributions are similar across test groups
# e.g. user demographics, device types, etc.


import pandas as pd
from scipy.stats import chi2_contingency

def categorical_balance_chi2(df: pd.DataFrame, group_col: str, cat_col: str):
    ct = pd.crosstab(df[group_col], df[cat_col])
    chi2, p, dof, _ = chi2_contingency(ct)
    return {"table": ct, "chi2": float(chi2), "p_value": float(p), "dof": int(dof)}

# -----Basic Data Quality Checks-----
# Checks for missing values, unexpected labels, duplicates, etc.

def basic_quality(df: pd.DataFrame):
    out = {}
    
    # Basic row count
    out["rows"] = int(len(df))
    
    # Missing values per column
    out["missing_by_col"] = df.isna().sum().to_dict()
    
    # Distribution of test groups
    if "test_group" in df.columns:
        out["groups"] = df["test_group"].value_counts().to_dict()
    else:
        out["groups"] = "test_group column NOT FOUND"
    
    # Distribution of outcome values
    if "converted" in df.columns:
        out["converted_values"] = df["converted"].value_counts().to_dict()
    else:
        out["converted_values"] = "converted column NOT FOUND"
    
    # Duplicate users if you have user_id in the Kaggle dataset
    if "user_id" in df.columns:
        out["duplicate_user_ids"] = int(df["user_id"].duplicated().sum())
    else:
        out["duplicate_user_ids"] = "user_id column NOT FOUND"
    
    return out
