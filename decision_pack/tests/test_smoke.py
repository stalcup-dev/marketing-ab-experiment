from pathlib import Path

from abpack.io import load_marketing_ab
from abpack.checks import srm_check


def test_load_and_srm_runs():
    # decision_pack/
    root = Path(__file__).resolve().parents[1]

    # Small committed fixture, not the big Kaggle CSV
    sample_path = root / "tests" / "fixtures" / "marketing_ab_sample.csv"

    df = load_marketing_ab(str(sample_path))
    res = srm_check(df, expected_split={"ad": 0.5, "psa": 0.5})

    assert isinstance(res.p_value, float)
    assert sum(res.observed.values()) == len(df)
