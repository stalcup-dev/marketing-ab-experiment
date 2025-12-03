from pathlib import Path

from abpack.io import load_marketing_ab
from abpack.checks import srm_check


def test_load_and_srm_runs():
    root = Path(__file__).resolve().parents[1]  # decision_pack/
    df = load_marketing_ab(str(root / "data" / "marketing_ab.csv"))

    res = srm_check(df, expected_split={"ad": 0.5, "psa": 0.5})

    assert isinstance(res.p_value, float)
    assert sum(res.observed.values()) == len(df)
