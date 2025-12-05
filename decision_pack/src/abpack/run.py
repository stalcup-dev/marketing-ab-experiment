from pathlib import Path

from abpack.io import load_marketing_ab
from abpack.checks import srm_check, basic_quality, categorical_balance_chi2
from abpack.stats import fmt_p


def main():
    # Resolve the "decision_pack/" directory regardless of where the script is executed from.
    # run.py is located at: decision_pack/src/abpack/run.py
    # parents[2] -> decision_pack/
    root = Path(__file__).resolve().parents[2]

    # Expected dataset location (you fixed earlier by copying/renaming into this folder)
    data_path = root / "data" / "marketing_ab.csv"

    # Where we write the markdown report
    report_path = root / "reports" / "integrity_report.md"

    # Load + normalize the Kaggle dataset (renames columns, coerces types, etc.)
    df = load_marketing_ab(str(data_path))

    # --- SRM (Sample Ratio Mismatch) diagnostics ---
    # SRM is only meaningful relative to an *intended* allocation.
    # Because we don't know Kaggle's intended split, we test:
    # 1) 50/50 reference (classic A/B expectation)
    # 2) 96/4 reference (holdout-style expectation) matching what the dataset appears to be
    srm_5050 = srm_check(df, expected_split={"ad": 0.5, "psa": 0.5})
    srm_9604 = srm_check(df, expected_split={"ad": 0.96, "psa": 0.04})

    # --- Basic data QA ---
    # Quick sanity checks: row counts, missingness summary, label distributions, duplicates (if user_id exists)
    q = basic_quality(df)

    # --- Distribution diagnostics (timing proxies) ---
    # These are not perfect "pre-treatment covariates" (they are derived from exposure),
    # but they're useful to detect non-comparable timing between groups.
    day = (
        categorical_balance_chi2(df, "test_group", "most_ads_day")
        if "most_ads_day" in df.columns
        else None
    )
    hour = (
        categorical_balance_chi2(df, "test_group", "most_ads_hour")
        if "most_ads_hour" in df.columns
        else None
    )

    # Build the markdown report line-by-line
    lines: list[str] = []
    lines.append("# Experiment Integrity Report\n")

    # ---------------- SRM SECTION ----------------
    lines.append("## SRM (Allocation Diagnostics)\n")

    # 50/50 reference split
    lines.append("### 50/50 reference (classic A/B)\n")
    lines.append(f"- Observed: {srm_5050.observed}\n")
    lines.append(
        f"- Expected (counts): "
        f"{ {k: round(v, 1) for k, v in srm_5050.expected.items()} }\n"
    )
    lines.append(f"- p-value: {fmt_p(srm_5050.p_value)}\n")
    lines.append(f"- Status: {'PASS' if srm_5050.pass_srm else 'FAIL'}\n\n")

    # 96/4 reference split
    lines.append("### 96/4 reference (holdout-style)\n")
    lines.append(f"- Observed: {srm_9604.observed}\n")
    lines.append(
        f"- Expected (counts): "
        f"{ {k: round(v, 1) for k, v in srm_9604.expected.items()} }\n"
    )
    lines.append(f"- p-value: {fmt_p(srm_9604.p_value)}\n")
    lines.append(f"- Status: {'PASS' if srm_9604.pass_srm else 'FAIL'}\n\n")

    # Interpretation guidance for the reader (PM / marketer / hiring manager)
    lines.append(
        "**Interpretation:** Failing 50/50 but passing 96/4 is consistent with a "
        "treatment-heavy holdout design rather than a balanced randomized 50/50 experiment.\n\n"
    )

    # ---------------- DATA QUALITY SECTION ----------------
    lines.append("## Data Quality\n")
    lines.append(f"- Rows: {q['rows']}\n")
    lines.append(f"- Groups: {q['groups']}\n")
    lines.append(f"- Converted values: {q['converted_values']}\n")

    # If user_id exists, report duplicates; otherwise be explicit that it wasn't available
    lines.append(f"- Duplicate user_ids: {q.get('duplicate_user_ids', 'user_id column NOT FOUND')}\n")
    lines.append("\n")

    # ---------------- DISTRIBUTION DIAGNOSTICS SECTION ----------------
    # In huge datasets, chi-square p-values often get extremely small; p-value alone can overstate importance.
    # Later improvement: add effect size (e.g., Cramér's V) to quantify practical difference.
    note_added = False
    if day:
        if not note_added:
            lines.append("_Cramér's V thresholds are rule-of-thumb guidelines._\n\n")
            note_added = True
        lines.append("## Balance / Distribution: most_ads_day\n")
        lines.append(f"- p-value: {fmt_p(day['p_value'])}\n\n")
        lines.append(
            "- effect_size (Cramér's V): "
            f"{day['cramers_v_formatted']} ({day['cramers_v_label']})\n\n"
        )

    if hour:
        if not note_added:
            lines.append("_Cramér's V thresholds are rule-of-thumb guidelines._\n\n")
            note_added = True
        lines.append("## Balance / Distribution: most_ads_hour\n")
        lines.append(f"- p-value: {fmt_p(hour['p_value'])}\n\n")
        lines.append(
            "- effect_size (Cramér's V): "
            f"{hour['cramers_v_formatted']} ({hour['cramers_v_label']})\n\n"
        )

    # Write report to disk (overwrite if it exists)
    report_path.write_text("".join(lines), encoding="utf-8")

    # Small console confirmation for your terminal logs
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
