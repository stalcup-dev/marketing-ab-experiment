# Decision Memo — Ad vs PSA (Kaggle marketing_AB)

## Decision
The Ad group shows a meaningful conversion advantage. This **may** represent true incremental impact under a properly randomized **holdout** design; however, the dataset does not document assignment/comparability, and timing distributions differ across groups. Therefore, treat this as **credible directional evidence** and avoid a strong causal claim until design/assignment is confirmed and stability checks pass.

## Impact (Directional; potentially causal if holdout is randomized)
- Control (psa) conversion: 1.79%
- Treatment (ad) conversion: 2.55%
- Lift: 0.77 pp (95% CI: 0.60 pp to 0.94 pp)
- Incremental conversions per 1M exposures: ~7,692

## Evidence Quality (Integrity)
- SRM vs 50/50 reference: FAIL (p=<1e-300)
- SRM vs holdout reference (96/4): PASS (p=0.999788)
- Observed allocation shares: ad ≈ 96.0% vs psa ≈ 4.0% (holdout-like).
- Timing distributions (day/hour) differ significantly across groups; with very large N, small practical differences can still yield tiny p-values.
- Data QA: labels are sane; no duplicate user_ids found.

## Risks / Caveats
- If holdout assignment is not randomized or not stable over time, time-based confounding can inflate/deflate apparent lift.
- Without true pre-treatment covariates (device/source/geo/traffic source), comparability is harder to verify.
- Independence assumptions may be violated if traffic is clustered by time/campaign; consider time-blocked checks or clustered SE in production.

## Next Steps (What I’d do in a real team)
- Confirm and document the intended design (randomized holdout vs selection rules), and monitor allocation over time.
- Quantify practical imbalance (e.g., effect size like Cramér’s V) and run time-sliced lift checks (by day/week) to verify stability.
- Add pre-treatment covariates + guardrails; consider stratified assignment by time blocks if timing effects matter.
- If design is confirmed randomized and stable: promote this result to a **causal** estimate and proceed with rollout + monitoring.
