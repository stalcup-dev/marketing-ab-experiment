import sys
from pathlib import Path
import math

# Make tests runnable even if PYTHONPATH isn't pre-configured
THIS_DIR = Path(__file__).resolve().parent
SRC_DIR = THIS_DIR.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from abpack.power import required_sample_size_two_proportion, plan_power  # noqa: E402


def test_required_n_matches_known_sanity_case():
    # Baseline from repo narrative (~1.79%), target lift ~0.77pp, alpha=0.05, power=0.80, 50/50
    nc, nt = required_sample_size_two_proportion(
        baseline_rate=0.0179,
        lift_pp=0.77,
        alpha=0.05,
        power=0.80,
        two_sided=True,
        treat_share=0.50,
    )
    # Normal-approx formulas vary slightly by convention; keep tolerance reasonable.
    assert 5200 <= nc <= 6200
    assert 5200 <= nt <= 6200
    assert (nc + nt) >= 10000


def test_smaller_lift_requires_more_samples():
    nc_big, nt_big = required_sample_size_two_proportion(0.02, 1.00, alpha=0.05, power=0.80)
    nc_small, nt_small = required_sample_size_two_proportion(0.02, 0.50, alpha=0.05, power=0.80)
    assert (nc_small + nt_small) > (nc_big + nt_big)


def test_higher_power_requires_more_samples():
    nc_80, nt_80 = required_sample_size_two_proportion(0.02, 0.50, alpha=0.05, power=0.80)
    nc_90, nt_90 = required_sample_size_two_proportion(0.02, 0.50, alpha=0.05, power=0.90)
    assert (nc_90 + nt_90) > (nc_80 + nt_80)


def test_runtime_days_computation():
    plan = plan_power(baseline_rate=0.02, lift_pp=0.50, daily_traffic=20000)
    assert plan.daily_traffic == 20000
    assert plan.est_runtime_days is not None
    assert plan.est_runtime_days > 0
    # sanity: total_n / daily_traffic = days
    assert math.isclose(plan.est_runtime_days, plan.total_n / 20000.0, rel_tol=1e-12)