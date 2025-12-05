from pathlib import Path

import pandas as pd
import pytest

from abpack.io import load_marketing_ab
from abpack.checks import srm_check, effect_size_label_cramers_v
from abpack import run as run_module


def test_load_and_srm_runs():
    # decision_pack/
    root = Path(__file__).resolve().parents[1]

    # Small committed fixture, not the big Kaggle CSV
    sample_path = root / "tests" / "fixtures" / "marketing_ab_sample.csv"

    df = load_marketing_ab(str(sample_path))
    res = srm_check(df, expected_split={"ad": 0.5, "psa": 0.5})

    assert isinstance(res.p_value, float)
    assert sum(res.observed.values()) == len(df)


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, "n/a"),
        (0.0, "negligible"),
        (0.10, "small"),
        (0.30, "medium"),
        (0.50, "large"),
    ],
)
def test_effect_size_label_boundaries(value, expected):
    assert effect_size_label_cramers_v(value) == expected


def test_integrity_report_includes_effect_size(monkeypatch):
    df = pd.DataFrame(
        {
            "test_group": ["ad", "psa", "ad", "psa"],
            "most_ads_day": ["Mon", "Tue", "Mon", "Wed"],
            "most_ads_hour": ["10", "11", "10", "12"],
            "converted": [0, 1, 0, 0],
            "user_id": [1, 2, 3, 4],
        }
    )

    monkeypatch.setattr(run_module, "load_marketing_ab", lambda _: df)

    captured = {}

    def fake_write_text(self, text, encoding="utf-8"):
        captured["text"] = text

    monkeypatch.setattr(Path, "write_text", fake_write_text)

    run_module.main()

    assert "- effect_size (Cramér's V):" in captured["text"]
