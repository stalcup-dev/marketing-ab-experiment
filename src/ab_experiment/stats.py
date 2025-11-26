# ============================================================
#  Future annotations allow type hints to refer to classes
#  that haven't been defined yet (helps with cleaner typing)
# ============================================================
from __future__ import annotations

# ============================================================
# dataclass automatically generates __init__, __repr__, etc.
# useful for packaging experiment results into one object
# ============================================================
from dataclasses import dataclass
from typing import Literal, Dict

# Core scientific/statistical stack
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats import proportion as sm_proportion
from statsmodels.stats.power import NormalIndPower


# ============================================================
# A simple container to store all lift metrics from a test.
# Keeps results structured for clean downstream use/reporting.
# ============================================================
@dataclass
class LiftResult:
    control_rate: float          # conversion rate of control group
    treatment_rate: float        # conversion rate of treatment group
    abs_lift: float              # absolute difference (treatment - control)
    rel_lift: float              # relative lift = abs_lift / control_rate
    control_n: int               # total users in control
    treatment_n: int             # total users in treatment
    control_converted: int       # converted users in control
    treatment_converted: int     # converted users in treatment


# ============================================================
# Computes conversion rates + absolute & relative lift
# This is your core business-impact metric generator.
# ============================================================
def compute_conversion_lift(
    df: pd.DataFrame,
    group_col: str = "test_group",      # column containing 'psa'/'ad'
    outcome_col: str = "converted",     # binary outcome column
    control_label: str = "psa",         # baseline group
    treatment_label: str = "ad",        # variant group
) -> LiftResult:
    
    # Group by test variant, compute number converted + total n
    grouped = (
        df.groupby(group_col)[outcome_col]
          .agg(["sum", "count"])                     # sum -> conversions , count -> total users
          .rename(columns={"sum": "converted", "count": "n"})
    )

    # Extract values for control & treatment
    control_conv = int(grouped.loc[control_label, "converted"])
    control_n = int(grouped.loc[control_label, "n"])
    treatment_conv = int(grouped.loc[treatment_label, "converted"])
    treatment_n = int(grouped.loc[treatment_label, "n"])

    # Compute conversion rates
    p_control = control_conv / control_n
    p_treatment = treatment_conv / treatment_n

    # Difference in conversion rates
    abs_lift = p_treatment - p_control
    rel_lift = abs_lift / p_control

    # Return as a structured dataclass
    return LiftResult(
        control_rate=p_control,
        treatment_rate=p_treatment,
        abs_lift=abs_lift,
        rel_lift=rel_lift,
        control_n=control_n,
        treatment_n=treatment_n,
        control_converted=control_conv,
        treatment_converted=treatment_conv,
    )


# ============================================================
# Runs a two-sample proportions Z-Test
# Used to validate whether observed lift is statistically reliable.
# ============================================================
def proportions_ztest(
    control_converted: int,
    control_total: int,
    treatment_converted: int,
    treatment_total: int,
    alternative: Literal["two-sided", "larger", "smaller"] = "two-sided",
) -> Dict[str, float]:

    # Input arrays for counts & sample sizes
    successes = np.array([treatment_converted, control_converted])
    nobs = np.array([treatment_total, control_total])

    # Perform Z-test for differences in conversion proportions
    z_stat, p_value = sm_proportion.proportions_ztest(
        count=successes,
        nobs=nobs,
        alternative=alternative,     # two-sided or directional hypothesis
    )
    return {"z_stat": float(z_stat), "p_value": float(p_value)}


# ============================================================
# Computes confidence interval for lift using Wald method
# Helps express uncertainty ranges around observed effect.
# ============================================================
def diff_proportions_ci(
    treatment_converted: int,
    treatment_n: int,
    control_converted: int,
    control_n: int,
    alpha: float = 0.05,            # 95% CI default
) -> Dict[str, float]:

    # Boundaries for how big/small lift could realistically be
    ci_low, ci_high = sm_proportion.confint_proportions_2indep(
        count1=treatment_converted,
        nobs1=treatment_n,
        count2=control_converted,
        nobs2=control_n,
        method="wald",              # classic CI for two independent proportions
        alpha=alpha,
    )
    return {"ci_low": float(ci_low), "ci_high": float(ci_high)}


# ============================================================
# Power calculation — tells how likely the test is to detect
# an effect of this size at chosen alpha.
# (You scale n later if planning experiment size.)
# ============================================================
def power_for_effect(
    p_control: float,
    p_treatment: float,
    alpha: float = 0.05,
) -> float:
    
    # Convert difference in proportions → standardized effect size
    effect_size = sm.stats.proportion_effectsize(p_treatment, p_control)
    
    power_calc = NormalIndPower()

    # nobs1=1.0 = baseline — user scales later to search sample sizes
    return float(power_calc.power(
        effect_size=effect_size,
        nobs1=1.0,
        ratio=1.0,          # equal group sizes assumption
        alpha=alpha,
    ))
