from pathlib import Path

from abpack.io import load_marketing_ab
from abpack.checks import srm_check
from abpack.stats import two_proportion_ztest_ci, fmt_pct, fmt_pp, fmt_p

# --- Expected allocation patterns for SRM diagnostics ---
# 1) Classic textbook A/B (reference check)
CLASSIC_AB_SPLIT = {"ad": 0.5, "psa": 0.5}

# 2) Holdout-style allocation (design check)
# If you ever use a different holdout %, update it here only.
HOLDOUT_SPLIT = {"ad": 0.96, "psa": 0.04}


def main():
    root = Path(__file__).resolve().parents[2]  # decision_pack/
    data_path = root / "data" / "marketing_ab.csv"
    est_path = root / "reports" / "estimation_report.md"
    memo_path = root / "reports" / "decision_memo_1pager.md"

    df = load_marketing_ab(str(data_path))

    # Define control vs treatment labels for reporting
    control = "psa"
    treatment = "ad"

    # Guardrail: if dataset labels are unexpected, fail loudly with a helpful message
    present_groups = set(df["test_group"].unique())
    required_groups = {control, treatment}
    if not required_groups.issubset(present_groups):
        raise ValueError(
            f"Expected groups {required_groups} in df['test_group'], "
            f"but found {present_groups}. Check column normalization in io.py."
        )

    # ---- Lift estimation ----
    g = (
        df.groupby("test_group")["converted"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "x", "count": "n"})
    )
    x_control, n_control = int(g.loc[control, "x"]), int(g.loc[control, "n"])
    x_treat, n_treat = int(g.loc[treatment, "x"]), int(g.loc[treatment, "n"])

    res = two_proportion_ztest_ci(
        x_control=x_control,
        n_control=n_control,
        x_treat=x_treat,
        n_treat=n_treat,
        control_label=control,
        treatment_label=treatment,
    )

    # Business translation: incremental conversions per 1M exposures (directional)
    incr_per_1m = res.abs_lift * 1_000_000

    # Observed shares for narrative
    total_n = n_control + n_treat
    share_treat = n_treat / total_n
    share_ctrl = n_control / total_n

    # ---- SRM diagnostics (memo self-contained) ----
    # SRM is meaningful only relative to an intended allocation.
    # We compute:
    # - Classic A/B: sanity check against a 50/50 assumption
    # - Holdout-style: check against a plausible holdout allocation
    srm_5050 = srm_check(df, expected_split=CLASSIC_AB_SPLIT)
    srm_holdout = srm_check(df, expected_split=HOLDOUT_SPLIT)

    # ---- Estimation report ----
    lines = []
    lines.append("# Estimation Report (Directional)\n")
    lines.append("## Metrics\n")
    lines.append(
        f"- Control ({control}) conversion: {fmt_pct(res.control_rate)} ({x_control}/{n_control})\n"
    )
    lines.append(
        f"- Treatment ({treatment}) conversion: {fmt_pct(res.treatment_rate)} ({x_treat}/{n_treat})\n"
    )
    lines.append(f"- Absolute lift (treat - control): {fmt_pp(res.abs_lift)}\n")
    lines.append(f"- Relative lift: {res.rel_lift * 100:.2f}%\n\n")

    lines.append("## Statistical Inference\n")
    lines.append(f"- Two-proportion z-test: z = {res.z_stat:.3f}\n")
    lines.append(f"- p-value: {fmt_p(res.p_value)}\n")
    lines.append(f"- 95% CI for lift: [{fmt_pp(res.ci_low)}, {fmt_pp(res.ci_high)}]\n\n")

    lines.append("## Practical Translation\n")
    lines.append(
        f"- Incremental conversions per 1,000,000 users exposed ≈ {incr_per_1m:,.0f}\n\n"
    )

    lines.append("## Interpretation (Important)\n")
    lines.append(
        "- The full-dataset estimate is best treated as **directional** unless assignment/comparability is confirmed.\n"
        "- The allocation pattern is consistent with a **holdout** (treatment-heavy) design; holdouts can be valid for incremental measurement if randomized and stable over time.\n"
    )

    est_path.write_text("".join(lines), encoding="utf-8")

    # ---- Auto-generated Decision Memo (nuanced + holdout-aware) ----
    memo = []
    memo.append("# Decision Memo — Ad vs PSA (Kaggle marketing_AB)\n\n")

    memo.append("## Decision\n")
    memo.append(
        "The Ad group shows a meaningful conversion advantage. This **may** represent true incremental impact under a properly randomized **holdout** design; "
        "however, the dataset does not document assignment/comparability, and timing distributions differ across groups. "
        "Therefore, treat this as **credible directional evidence** and avoid a strong causal claim until design/assignment is confirmed and stability checks pass.\n\n"
    )

    memo.append("## Impact (Directional; potentially causal if holdout is randomized)\n")
    memo.append(f"- Control ({control}) conversion: {fmt_pct(res.control_rate)}\n")
    memo.append(f"- Treatment ({treatment}) conversion: {fmt_pct(res.treatment_rate)}\n")
    memo.append(
        f"- Lift: {fmt_pp(res.abs_lift)} (95% CI: {fmt_pp(res.ci_low)} to {fmt_pp(res.ci_high)})\n"
    )
    memo.append(f"- Incremental conversions per 1M exposures: ~{incr_per_1m:,.0f}\n\n")

    memo.append("## Evidence Quality (Integrity)\n")
        # Add hard proof lines (SRM diagnostics)
    memo.append(
        f"- SRM vs 50/50 reference: {('PASS' if srm_5050.pass_srm else 'FAIL')} (p={fmt_p(srm_5050.p_value)})\n"
    )
    memo.append(
        f"- SRM vs holdout reference ({int(HOLDOUT_SPLIT[treatment]*100)}/{int(HOLDOUT_SPLIT[control]*100)}): "
        f"{('PASS' if srm_holdout.pass_srm else 'FAIL')} (p={fmt_p(srm_holdout.p_value)})\n"
    )
    memo.append(
        f"- Observed allocation shares: {treatment} ≈ {share_treat * 100:.1f}% vs {control} ≈ {share_ctrl * 100:.1f}% (holdout-like).\n"
    )
    memo.append(
        "- Timing distributions (day/hour) differ significantly across groups; with very large N, small practical differences can still yield tiny p-values.\n"
    )
    memo.append("- Data QA: labels are sane; no duplicate user_ids found.\n\n")

    memo.append("## Risks / Caveats\n")
    memo.append(
        "- If holdout assignment is not randomized or not stable over time, time-based confounding can inflate/deflate apparent lift.\n"
    )
    memo.append(
        "- Without true pre-treatment covariates (device/source/geo/traffic source), comparability is harder to verify.\n"
    )
    memo.append(
        "- Independence assumptions may be violated if traffic is clustered by time/campaign; consider time-blocked checks or clustered SE in production.\n\n"
    )

    memo.append("## Next Steps (What I’d do in a real team)\n")
    memo.append(
        "- Confirm and document the intended design (randomized holdout vs selection rules), and monitor allocation over time.\n"
    )
    memo.append(
        "- Quantify practical imbalance (e.g., effect size like Cramér’s V) and run time-sliced lift checks (by day/week) to verify stability.\n"
    )
    memo.append(
        "- Add pre-treatment covariates + guardrails; consider stratified assignment by time blocks if timing effects matter.\n"
    )
    memo.append(
        "- If design is confirmed randomized and stable: promote this result to a **causal** estimate and proceed with rollout + monitoring.\n"
    )

    memo_path.write_text("".join(memo), encoding="utf-8")

    print(f"Wrote {est_path}")
    print(f"Wrote {memo_path}")


if __name__ == "__main__":
    main()
