# Sequential Testing Note (and why “peeking” breaks p-values)

## What “peeking” is
“Peeking” = repeatedly checking statistical significance (p-values / CIs) during a test and stopping early when results look good.

Example: you planned to run 14 days, but you check p-values daily and ship on day 3 because p < 0.05.

## Why peeking inflates false positives (brief + practical)
A p-value threshold like 0.05 assumes **one pre-specified analysis** at a **fixed horizon**.

If you test the same hypothesis over and over (e.g., every day), you’ve turned one hypothesis test into many chances to “get lucky.”
Result: the real probability of a false positive becomes **greater than 5%**.

You can think of it as a multiple-comparisons problem over time.

## One safe approach (choose one): Fixed-horizon (recommended default)
### Rule
1. **Decide the sample size up front** (via power planning) + lock the stop condition.
2. **Do not run significance tests until the stop condition is met.**
3. At the horizon, run the planned analysis once and make the ship decision.

This keeps your Type I error (false positives) aligned with alpha.

## Simple decision rule (example)
Ship **only if all are true**:
1. Direction: lift is positive (Treatment − Control > 0)
2. Statistical evidence at the horizon: p < alpha (or CI excludes 0 in the positive direction)
3. Guardrails pass (no material regressions on safety metrics)
Otherwise: **No-ship** (or iterate and retest).

## How to enforce this in practice (what real teams do)
### Pre-commit the plan
- Put the stop condition in the experiment spec:
  - “Stop when total N >= X AND at least Y full days have elapsed (avoids day-of-week skew).”
- Capture alpha, power, primary metric, and planned segmentation.

### Operational enforcement
- Daily monitoring is allowed for **data quality** and **guardrails** only (SRM, logging health, obvious breaks).
- Block “p-value dashboards” until the horizon:
  - Only compute p-values in the final analysis script.
  - Or gate a report-generation step so it only runs once `N >= X`.

### If you *must* look early
Then you need a sequential method (alpha-spending / Bayesian / group-sequential). Don’t pretend fixed-horizon p-values remain valid.
