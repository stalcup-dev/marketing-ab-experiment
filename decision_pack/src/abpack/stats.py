from dataclasses import dataclass
from math import sqrt
from typing import Dict  # NOTE: unused import in this snippet; safe to delete
from scipy.stats import norm  # normal distribution utilities (CDF/PPF) for z-test + CI


# -------------------------
# Result container (strong practice for clean APIs)
# -------------------------
@dataclass
class TwoPropResult:
    # Labels help when reporting (e.g., "ad" vs "psa")
    control_label: str
    treatment_label: str

    # Sample sizes (n) and successes (x) for each group
    n_control: int
    x_control: int
    n_treat: int
    x_treat: int

    # Observed conversion rates
    control_rate: float
    treatment_rate: float

    # Lift metrics
    abs_lift: float      # p_treat - p_control (absolute difference in proportions)
    rel_lift: float      # (p_treat - p_control) / p_control (relative lift)

    # Inference outputs
    z_stat: float        # z statistic for two-proportion z-test (pooled SE under H0)
    p_value: float       # two-sided p-value

    # Confidence interval for the absolute lift (difference in proportions)
    ci_low: float
    ci_high: float


# -------------------------
# Two-proportion z-test + CI
# -------------------------
def two_proportion_ztest_ci(
    *,
    x_control: int,
    n_control: int,
    x_treat: int,
    n_treat: int,
    control_label: str = "control",
    treatment_label: str = "treatment",
    alpha: float = 0.05,
) -> TwoPropResult:
    """
    Runs:
      1) Two-proportion z-test using pooled standard error (correct under H0: p1 == p2)
      2) (1 - alpha) confidence interval for (p2 - p1) using unpooled standard error
         (very common for reporting the uncertainty in the observed difference)

    Returns a TwoPropResult dataclass with rates, lifts, z, p-value, and CI.
    """

    # Guardrails: you can’t compute rates with non-positive denominators
    if n_control <= 0 or n_treat <= 0:
        raise ValueError("n_control and n_treat must be > 0")

    # Compute observed conversion rates for each group:
    # p1 = control conversion rate, p2 = treatment conversion rate
    p1 = x_control / n_control
    p2 = x_treat / n_treat

    # Absolute difference (treatment - control)
    diff = p2 - p1

    # ---- Hypothesis test part (z-test) ----
    # Under H0 (no effect), we assume both groups share the *same* true rate p.
    # The best estimate of that shared p under H0 is the pooled rate:
    pooled = (x_control + x_treat) / (n_control + n_treat)

    # Pooled standard error for difference in proportions under H0:
    # SE_pooled = sqrt( p*(1-p) * (1/n1 + 1/n2) )
    se_pooled = sqrt(pooled * (1 - pooled) * (1 / n_control + 1 / n_treat))

    # z-statistic = observed difference / SE under H0
    # If SE is 0 (can happen if pooled is 0 or 1), define z as 0 to avoid division by zero.
    z = diff / se_pooled if se_pooled > 0 else 0.0

    # Two-sided p-value from z:
    # p = 2 * P(Z >= |z|)
    p_val = 2 * (1 - norm.cdf(abs(z)))

    # ---- Confidence interval part (CI for effect size) ----
    # For CI, you typically use the *unpooled* SE because you’re estimating the
    # uncertainty around the observed difference (not forcing H0 true).
    # SE_unpooled = sqrt( p1(1-p1)/n1 + p2(1-p2)/n2 )
    se_unpooled = sqrt(p1 * (1 - p1) / n_control + p2 * (1 - p2) / n_treat)

    # z critical value for the desired confidence level:
    # alpha=0.05 -> 95% CI -> zcrit ~ 1.96
    zcrit = norm.ppf(1 - alpha / 2)

    # CI for diff: diff ± zcrit * SE_unpooled
    ci_low = diff - zcrit * se_unpooled
    ci_high = diff + zcrit * se_unpooled

    # Relative lift (careful if control rate is 0)
    rel = diff / p1 if p1 > 0 else float("inf")

    # Package everything into a structured result for clean downstream reporting
    return TwoPropResult(
        control_label=control_label,
        treatment_label=treatment_label,
        n_control=n_control,
        x_control=x_control,
        n_treat=n_treat,
        x_treat=x_treat,
        control_rate=p1,
        treatment_rate=p2,
        abs_lift=diff,
        rel_lift=rel,
        z_stat=z,
        p_value=p_val,
        ci_low=ci_low,
        ci_high=ci_high,
    )


# -------------------------
# Formatting helpers (report-friendly)
# -------------------------
def fmt_pct(x: float, decimals: int = 2) -> str:
    # Converts 0.1234 -> "12.34%"
    return f"{100 * x:.{decimals}f}%"


def fmt_pp(x: float, decimals: int = 2) -> str:
    """Percentage points (e.g., 0.0076 -> 0.76 pp)."""
    # Converts an absolute proportion difference to "pp" display
    return f"{100 * x:.{decimals}f} pp"


def fmt_p(p: float) -> str:
    # Avoid ugly "0.0" due to floating underflow; show an ultra-small floor instead
    return "<1e-300" if p == 0.0 else f"{p:.6g}"
