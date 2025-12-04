from __future__ import annotations

import argparse
from pathlib import Path

from abpack.power import mde_pp_for_n_two_proportion, plan_power


def _fmt_pct(x: float) -> str:
    return f"{100.0 * x:.2f}%"


def _fmt_pp(pp: float) -> str:
    return f"{pp:.2f} pp"


def _fmt_int(n: int) -> str:
    return f"{n:,}"


def build_power_report_md(
    baseline_rate: float,
    lift_pp: float,
    alpha: float,
    power: float,
    two_sided: bool,
    treat_share: float,
    daily_traffic: int | None,
) -> str:
    plan = plan_power(
        baseline_rate=baseline_rate,
        lift_pp=lift_pp,
        alpha=alpha,
        power=power,
        two_sided=two_sided,
        treat_share=treat_share,
        daily_traffic=daily_traffic,
    )

    lines: list[str] = []
    lines.append("# Power + MDE Planning\n")
    lines.append(
        "This planning note sizes a 2-arm conversion experiment using a normal-approx "
        "two-proportion z-test.\n"
    )

    lines.append("## Inputs\n")
    lines.append(f"- Baseline conversion rate: **{_fmt_pct(plan.baseline_rate)}**\n")
    lines.append(f"- Desired lift (absolute): **{_fmt_pp(plan.lift_pp)}**\n")
    lines.append(f"- Alpha: **{plan.alpha:.3f}** ({'two-sided' if plan.two_sided else 'one-sided'})\n")
    lines.append(f"- Power: **{plan.power:.2f}**\n")
    lines.append(f"- Traffic split (treatment share): **{plan.treat_share:.2f}**\n")
    if daily_traffic is not None:
        lines.append(f"- Daily eligible traffic: **{_fmt_int(daily_traffic)} users/day**\n")
    lines.append("\n")

    lines.append("## Assumptions (explicit)\n")
    lines.append("- Binary outcome per user (converted = 0/1), independent users.\n")
    lines.append("- Stable baseline rate during the test window.\n")
    lines.append("- Fixed-horizon analysis (no repeated peeking); otherwise alpha inflates.\n")
    lines.append("- Z-test normal approximation is acceptable given expected counts.\n")
    lines.append("\n")

    lines.append("## Output: required sample size\n")
    lines.append(f"- Control N: **{_fmt_int(plan.n_control)}**\n")
    lines.append(f"- Treatment N: **{_fmt_int(plan.n_treatment)}**\n")
    lines.append(f"- Total N: **{_fmt_int(plan.total_n)}**\n")
    lines.append("\n")

    if plan.est_runtime_days is not None:
        days = plan.est_runtime_days
        hours = days * 24.0
        lines.append("## Estimated runtime (given daily traffic)\n")
        lines.append(f"- Estimated runtime: **{days:.2f} days** (~{hours:.1f} hours)\n\n")

    # Bonus: if you ran exactly this planned N, what's the implied MDE sanity check?
    mde_pp = mde_pp_for_n_two_proportion(
        baseline_rate=baseline_rate,
        n_control=plan.n_control,
        n_treatment=plan.n_treatment,
        alpha=alpha,
        power=power,
        two_sided=two_sided,
    )
    lines.append("## Sanity check: implied MDE at this N\n")
    lines.append(
        f"- With these sample sizes, the MDE is **{_fmt_pp(mde_pp)}** "
        "(should be ~equal to the target lift, up to rounding/approximation).\n"
    )
    lines.append("\n")

    lines.append("## Example run\n")
    lines.append("```bash\n")
    lines.append(
        "cd decision_pack/src\n"
        "python -m abpack.run_power \\\n"
        "  --baseline 0.0179 \\\n"
        "  --lift-pp 0.77 \\\n"
        "  --alpha 0.05 \\\n"
        "  --power 0.80 \\\n"
        "  --daily-traffic 10000 \\\n"
        "  --treat-share 0.50\n"
    )
    lines.append("```\n")

    return "".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Power + MDE planning for a 2-arm conversion test.")
    p.add_argument("--baseline", type=float, required=True, help="Baseline conversion rate (e.g., 0.0179).")
    p.add_argument("--lift-pp", type=float, required=True, help="Desired absolute lift in percentage points (e.g., 0.77).")
    p.add_argument("--alpha", type=float, default=0.05, help="Significance level (default: 0.05).")
    p.add_argument("--power", type=float, default=0.80, help="Target power (default: 0.80).")
    p.add_argument("--one-sided", action="store_true", help="Use a one-sided alpha (default is two-sided).")
    p.add_argument("--treat-share", type=float, default=0.50, help="Treatment traffic share, in (0,1) (default: 0.50).")
    p.add_argument("--daily-traffic", type=int, default=None, help="Eligible users/day (optional).")
    args = p.parse_args()

    root = Path(__file__).resolve().parents[2]  # decision_pack/
    report_path = root / "reports" / "power_mde_planning.md"

    md = build_power_report_md(
        baseline_rate=args.baseline,
        lift_pp=args.lift_pp,
        alpha=args.alpha,
        power=args.power,
        two_sided=not args.one_sided,
        treat_share=args.treat_share,
        daily_traffic=args.daily_traffic,
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(md, encoding="utf-8")

    print(f"Wrote: {report_path}")
    print("Top-line:")
    # quick stdout summary
    plan = plan_power(
        baseline_rate=args.baseline,
        lift_pp=args.lift_pp,
        alpha=args.alpha,
        power=args.power,
        two_sided=not args.one_sided,
        treat_share=args.treat_share,
        daily_traffic=args.daily_traffic,
    )
    print(f"  Control N={plan.n_control:,}  Treatment N={plan.n_treatment:,}  Total N={plan.total_n:,}")
    if plan.est_runtime_days is not None:
        print(f"  Est. runtime ~ {plan.est_runtime_days:.2f} days")


if __name__ == "__main__":
    main()
