from dataclasses import dataclass
from typing import List, Literal
import pandas as pd
import numpy as np


@dataclass
class StratifiedLift:
    strata: List[str]
    pooled_lift_pp: float
    ci_low_pp: float
    ci_high_pp: float
    strata_table: pd.DataFrame  # details per stratum


def _coerce_binary_outcome(series: pd.Series, name: str) -> pd.Series:
    """
    Coerce y_col into {0,1} ints, or raise a clear error.
    Accepts: bool, 0/1 numeric, or common strings ("0","1","true","false","yes","no").
    """
    s = series.copy()

    # Disallow NA silently sneaking in
    if s.isna().any():
        raise ValueError(f"{name} contains missing values (NA). Fill/drop before stratified_lift().")

    # Bool -> int
    if pd.api.types.is_bool_dtype(s):
        return s.astype(int)

    # Numeric -> must already be 0/1
    if pd.api.types.is_numeric_dtype(s):
        vals = set(pd.unique(s))
        if not vals.issubset({0, 1}):
            preview = sorted(list(vals))[:10]
            raise ValueError(f"{name} must be binary (0/1). Found values like: {preview}")
        return s.astype(int)

    # Object/string -> attempt mapping common labels to 0/1
    if pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s):
        mapping = {
            "0": 0, "1": 1,
            "false": 0, "true": 1,
            "no": 0, "yes": 1,
            "n": 0, "y": 1,
        }
        lowered = s.astype(str).str.strip().str.lower()
        mapped = lowered.map(mapping)
        if mapped.isna().any():
            bad = sorted(lowered[mapped.isna()].unique().tolist())[:10]
            raise ValueError(
                f"{name} must be binary. Could not map these values to 0/1: {bad}. "
                f"Use 0/1, bool, or yes/no/true/false."
            )
        return mapped.astype(int)

    raise ValueError(f"{name} must be binary (0/1) or bool. Got dtype={s.dtype}.")


def stratified_lift(
    df: pd.DataFrame,
    strata_cols: List[str],
    group_col: str = "test_group",
    y_col: str = "converted",
    control: str = "psa",
    treatment: str = "ad",
    min_n_per_arm: int = 1,  # keep legacy behavior by default; set 30+ if you want stability
    weighting: Literal["n_total", "inv_var"] = "n_total",  # legacy default
    alpha: float = 0.05,
) -> StratifiedLift:
    """
    Stratified lift (treatment - control) pooled across strata with a normal-approx CI.

    - Validates/converts y_col to binary {0,1}
    - Optionally drops small strata via min_n_per_arm
    - Supports weights: n_total (legacy) or inv_var (inverse-variance)
    """
    d = df.copy()

    # Basic column validation
    needed = set(strata_cols + [group_col, y_col])
    missing = needed - set(d.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    # Coerce outcome to binary {0,1}
    d[y_col] = _coerce_binary_outcome(d[y_col], y_col)

    rows = []
    for keys, g in d.groupby(strata_cols, dropna=False):
        gc = g.loc[g[group_col] == control, y_col]
        gt = g.loc[g[group_col] == treatment, y_col]

        n_c, n_t = int(gc.shape[0]), int(gt.shape[0])
        if n_c < min_n_per_arm or n_t < min_n_per_arm:
            continue

        p_c = float(gc.mean())
        p_t = float(gt.mean())
        lift = p_t - p_c  # proportion points

        # Normal-approx variance for diff in proportions
        var = (p_t * (1.0 - p_t) / n_t) + (p_c * (1.0 - p_c) / n_c)

        # Normalize keys for 1 vs many strata cols
        key_tuple = keys if isinstance(keys, tuple) else (keys,)
        key_dict = dict(zip(strata_cols, key_tuple))

        rows.append(
            {
                **key_dict,
                "n_c": n_c,
                "n_t": n_t,
                "n_total": n_c + n_t,
                "p_c": p_c,
                "p_t": p_t,
                "lift": lift,
                "var": var,
            }
        )

    tab = pd.DataFrame(rows)
    if tab.empty:
        raise ValueError("No strata had both control and treatment samples meeting min_n_per_arm.")

    # Choose weights
    if weighting == "n_total":
        w = tab["n_total"].astype(float)
    elif weighting == "inv_var":
        # Guard against var=0 (can happen if p is 0 or 1 in both arms)
        eps = 1e-12
        w = 1.0 / (tab["var"].astype(float) + eps)
    else:
        raise ValueError("weighting must be 'n_total' or 'inv_var'")

    W = float(np.sum(w))
    a = w / W  # normalized weights

    pooled = float(np.sum(a * tab["lift"]))

    # Var(weighted mean) = sum(a_i^2 * var_i)
    pooled_var = float(np.sum((a**2) * tab["var"].astype(float)))
    se = float(np.sqrt(pooled_var))

    # Two-sided normal CI
    # For alpha=0.05, z ~= 1.96
    from scipy.stats import norm
    z = float(norm.ppf(1.0 - alpha / 2.0))

    ci_low = pooled - z * se
    ci_high = pooled + z * se

    tab["weight"] = w
    tab = tab.sort_values(["n_total"], ascending=False).reset_index(drop=True)

    return StratifiedLift(
        strata=strata_cols,
        pooled_lift_pp=float(pooled),
        ci_low_pp=float(ci_low),
        ci_high_pp=float(ci_high),
        strata_table=tab,
    )
