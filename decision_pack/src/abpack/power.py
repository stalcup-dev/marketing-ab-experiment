# from __future__ import annotations
# - Postpones evaluation of type hints (annotations) until later.
# - Helps avoid forward-reference issues and reduces import-order headaches.
from __future__ import annotations

# dataclasses:
# - @dataclass generates __init__, __repr__, comparisons, etc.
# - frozen=True makes instances immutable (safer for “result objects”).
from dataclasses import dataclass

import math  # sqrt, ceil, isnan, etc.

# typing:
# - Optional[T] means “T or None”
# - Tuple[int, int] means a 2-item tuple of ints
from typing import Optional, Tuple

# scipy.stats.norm:
# - norm.ppf(q) is the inverse-CDF (quantile) function for standard normal.
# - Used to get z-critical values for alpha (significance) and power.
from scipy.stats import norm


@dataclass(frozen=True)
class PowerPlan:
    """
    Power / sample size plan for a 2-arm conversion A/B test (two-proportion z-test),
    using a normal approximation.

    Conventions:
    - Rates are probabilities in [0, 1] (e.g., 0.0179 for 1.79%)
    - lift_pp is in *percentage points* (pp), e.g., 0.77 means +0.0077 absolute rate
    """

    # --- Inputs / assumptions ---
    baseline_rate: float     # Control conversion rate, e.g. 0.0179
    treatment_rate: float    # Treatment conversion rate = baseline_rate + lift_pp/100
    lift_pp: float           # Lift in *percentage points* (pp), e.g. 0.77
    alpha: float             # Type I error rate (false positive rate), e.g. 0.05
    power: float             # 1 - beta (true positive probability), e.g. 0.80
    two_sided: bool          # Two-sided test? if True, split alpha across two tails
    treat_share: float       # Fraction of traffic assigned to treatment (0 < share < 1)

    # --- Outputs (computed sample sizes) ---
    n_control: int           # Required sample size in control group
    n_treatment: int         # Required sample size in treatment group
    total_n: int             # Total required sample size

    # --- Optional planning helpers ---
    daily_traffic: Optional[int] = None   # Total daily eligible traffic (if known)
    est_runtime_days: Optional[float] = None  # Estimated days to reach total_n


def _check_prob(name: str, x: float) -> None:
    """
    Validate that x is a number and in [0, 1].

    Used for probabilities: baseline_rate, alpha, power, treat_share (with extra checks).
    """
    # Ensure it's numeric and not NaN
    if not isinstance(x, (int, float)) or math.isnan(float(x)):
        raise TypeError(f"{name} must be a number. Got: {type(x)}")

    # Ensure probability bounds
    if x < 0 or x > 1:
        raise ValueError(f"{name} must be in [0, 1]. Got: {x}")


def _check_rate_pp(name: str, x: float) -> None:
    """
    Validate that a "rate in percentage points" is numeric and > 0.

    lift_pp is expected to be positive (this planner assumes you want to detect an increase).
    """
    if not isinstance(x, (int, float)) or math.isnan(float(x)):
        raise TypeError(f"{name} must be a number. Got: {type(x)}")
    if x <= 0:
        raise ValueError(f"{name} must be > 0. Got: {x}")


def _check_alpha_power(alpha: float, power: float) -> None:
    """
    Validate alpha and power are valid probabilities in (0, 1).
    Using open interval (0,1) because alpha=0 or 1 is nonsensical; same for power.
    """
    _check_prob("alpha", alpha)
    _check_prob("power", power)
    if alpha <= 0 or alpha >= 1:
        raise ValueError(f"alpha must be in (0, 1). Got: {alpha}")
    if power <= 0 or power >= 1:
        raise ValueError(f"power must be in (0, 1). Got: {power}")


def _check_treat_share(treat_share: float) -> None:
    """
    Validate treatment allocation share is in (0, 1).

    treat_share=0 or 1 would mean “no treatment” or “no control”—invalid for A/B.
    """
    _check_prob("treat_share", treat_share)
    if treat_share <= 0 or treat_share >= 1:
        raise ValueError(f"treat_share must be in (0, 1). Got: {treat_share}")


def _z_alpha(alpha: float, two_sided: bool) -> float:
    """
    Convert alpha to a z value (critical threshold).

    - Two-sided: alpha split into two tails -> quantile = 1 - alpha/2
    - One-sided: alpha in one tail -> quantile = 1 - alpha
    """
    q = 1 - (alpha / 2 if two_sided else alpha)
    return float(norm.ppf(q))


def _z_beta(power: float) -> float:
    """
    Convert desired power to a z value.

    power = P(reject H0 | true effect), so we take z at that quantile.
    """
    return float(norm.ppf(power))


def required_sample_size_two_proportion(
    baseline_rate: float,
    lift_pp: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sided: bool = True,
    treat_share: float = 0.50,
) -> Tuple[int, int]:
    """
    Returns (n_control, n_treatment) required to detect baseline_rate + lift_pp
    with specified alpha/power using a two-proportion z-test (normal approximation).

    Notes:
    - lift_pp is in percentage points (pp): 0.77 => +0.0077 absolute rate
    - treat_share is fraction of traffic in treatment; control_share = 1 - treat_share
    """
    # --- Validate inputs ---
    _check_prob("baseline_rate", baseline_rate)
    _check_rate_pp("lift_pp", lift_pp)
    _check_alpha_power(alpha, power)
    _check_treat_share(treat_share)

    # Convert percentage points -> absolute probability delta
    # Example: 0.77pp -> 0.0077 absolute
    delta = lift_pp / 100.0

    # p1: control conversion rate, p2: treatment conversion rate
    p1 = float(baseline_rate)
    p2 = p1 + delta

    # Treatment rate must also be a valid probability
    if p2 <= 0 or p2 >= 1:
        raise ValueError(
            f"treatment_rate must be in (0, 1). Got baseline={p1}, lift_pp={lift_pp} -> p2={p2}"
        )

    # Allocation math:
    # treat_share = n_treat / (n_control + n_treat)
    # control_share = 1 - treat_share
    control_share = 1.0 - float(treat_share)

    # r = n_treat / n_control (sample size ratio)
    # Example: treat_share=0.5 => r=1
    # Example: treat_share=0.8 => r=4 (treatment 4x control)
    r = float(treat_share) / float(control_share)

    # Convert alpha and power into z-values
    z_a = _z_alpha(alpha, two_sided=two_sided)
    z_b = _z_beta(power)

    # Pooled rate proxy (common approximation to plug into variance)
    # Weighted by allocation ratio r.
    pbar = (p1 + r * p2) / (1.0 + r)

    # term1: alpha (false positive control) component
    # sqrt(pbar*(1-pbar)*(1 + 1/r)) adjusts for 2-sample comparison with unequal sizing.
    term1 = z_a * math.sqrt(pbar * (1.0 - pbar) * (1.0 + 1.0 / r))

    # term2: power (false negative control) component
    # Uses unpooled variances p1*(1-p1) and p2*(1-p2), adjusted by ratio r.
    term2 = z_b * math.sqrt(p1 * (1.0 - p1) + (p2 * (1.0 - p2)) / r)

    # Solve sample size:
    # n_control = ((term1 + term2)^2) / delta^2
    # n_treat scales by r (n_treat = r * n_control)
    n_control = ((term1 + term2) ** 2) / (delta**2)
    n_treat = n_control * r

    # Ceiling to ensure we have *at least* enough samples
    return int(math.ceil(n_control)), int(math.ceil(n_treat))


def mde_pp_for_n_two_proportion(
    baseline_rate: float,
    n_control: int,
    n_treatment: int,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sided: bool = True,
) -> float:
    """
    Compute the minimum detectable effect (MDE) in percentage points (pp)
    for a given (n_control, n_treatment), baseline rate, alpha, and power.

    This numerically inverts required_sample_size_two_proportion.
    """
    # Validate baseline/alpha/power
    _check_prob("baseline_rate", baseline_rate)
    _check_alpha_power(alpha, power)

    # Validate sample sizes
    if n_control <= 0 or n_treatment <= 0:
        raise ValueError("n_control and n_treatment must be positive integers.")

    # Infer treatment share from the given n's
    treat_share = n_treatment / (n_control + n_treatment)

    # Binary search bounds for lift_pp (in pp)
    # low ~ 0, high limited by remaining headroom to 100% conversion, and capped at 50pp.
    low = 1e-6
    high = min((1.0 - baseline_rate) * 100.0 - 1e-6, 50.0)

    def required_n_at(lift_pp: float) -> int:
        """
        Given a candidate lift_pp, compute required total N for that lift,
        using the same alpha/power and the inferred treat_share.
        """
        nc, nt = required_sample_size_two_proportion(
            baseline_rate=baseline_rate,
            lift_pp=lift_pp,
            alpha=alpha,
            power=power,
            two_sided=two_sided,
            treat_share=treat_share,
        )
        # Compare total N since treat_share is embedded in the call
        return nc + nt

    target_total = int(n_control + n_treatment)

    # Ensure “high” is big enough (i.e., lift large enough) so required N <= target_total.
    # If high is too small, required_n_at(high) will be > target_total.
    for _ in range(30):
        if required_n_at(high) <= target_total:
            break
        # Increase high (up to the theoretical max lift)
        high = min(high * 1.5, (1.0 - baseline_rate) * 100.0 - 1e-6)
    else:
        # for-else: this else runs if the loop never broke (couldn't bracket)
        raise RuntimeError("Could not bracket MDE. Try increasing n or adjusting caps.")

    # Binary search (bisection):
    # We want smallest lift such that required_n_at(lift) <= target_total.
    for _ in range(60):
        mid = (low + high) / 2.0
        if required_n_at(mid) > target_total:
            # mid lift still needs too many samples -> lift is too small -> move low up
            low = mid
        else:
            # mid lift is detectable with our N -> try smaller lift -> move high down
            high = mid

    # “high” converges to the MDE in pp
    return float(high)


def plan_power(
    baseline_rate: float,
    lift_pp: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sided: bool = True,
    treat_share: float = 0.50,
    daily_traffic: Optional[int] = None,
) -> PowerPlan:
    """
    Convenience wrapper:
    - Computes required sample size (n_control, n_treat)
    - Computes total N
    - Optionally estimates runtime given daily_traffic
    - Returns a PowerPlan dataclass with everything populated
    """
    # Compute required sample sizes
    n_control, n_treat = required_sample_size_two_proportion(
        baseline_rate=baseline_rate,
        lift_pp=lift_pp,
        alpha=alpha,
        power=power,
        two_sided=two_sided,
        treat_share=treat_share,
    )
    total_n = n_control + n_treat

    # Optional runtime estimation
    est_days: Optional[float] = None
    if daily_traffic is not None:
        if daily_traffic <= 0:
            raise ValueError("daily_traffic must be a positive integer.")
        est_days = total_n / float(daily_traffic)

    # Return an immutable structured result
    return PowerPlan(
        baseline_rate=float(baseline_rate),
        treatment_rate=float(baseline_rate) + float(lift_pp) / 100.0,
        lift_pp=float(lift_pp),
        alpha=float(alpha),
        power=float(power),
        two_sided=bool(two_sided),
        treat_share=float(treat_share),
        n_control=int(n_control),
        n_treatment=int(n_treat),
        total_n=int(total_n),
        daily_traffic=int(daily_traffic) if daily_traffic is not None else None,
        est_runtime_days=est_days,
    )
