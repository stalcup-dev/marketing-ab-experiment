# Estimation Report (Directional)
## Metrics
- Control (psa) conversion: 1.79% (420/23524)
- Treatment (ad) conversion: 2.55% (14423/564577)
- Absolute lift (treat - control): 0.77 pp
- Relative lift: 43.09%

## Statistical Inference
- Two-proportion z-test: z = 7.370
- p-value: 1.7053e-13
- 95% CI for lift: [0.60 pp, 0.94 pp]

## Practical Translation
- Incremental conversions per 1,000,000 users exposed ≈ 7,692

## Robustness: Stratified lift (timing adjustment)
We recompute lift **within each time stratum** (day/hour) and then pool across strata.
If pooled stratified lift is close to the naive lift, the signal is more stable. If it collapses or flips, the naive lift was likely driven by timing imbalance.

- Naive lift (full dataset): **0.77 pp**

### Stratified by `most_ads_day`
- Pooled stratified lift: **0.78 pp** (95% CI 0.60 pp to 0.95 pp)
- Difference vs naive: **0.01 pp**
- Interpretation: Stratified ≈ naive (signal looks **more stable** across timing).
- Top strata by sample weight:
  - `most_ads_day`=Friday: control 1.63% (3803), treatment 2.25% (88805), lift 0.62 pp
  - `most_ads_day`=Monday: control 2.26% (3502), treatment 3.32% (83571), lift 1.07 pp
  - `most_ads_day`=Sunday: control 2.06% (3059), treatment 2.46% (82332), lift 0.40 pp
  - `most_ads_day`=Thursday: control 2.02% (3905), treatment 2.16% (79077), lift 0.14 pp
  - `most_ads_day`=Saturday: control 1.40% (2858), treatment 2.13% (78802), lift 0.73 pp

### Stratified by `most_ads_hour`
- Pooled stratified lift: **0.78 pp** (95% CI 0.61 pp to 0.95 pp)
- Difference vs naive: **0.01 pp**
- Interpretation: Stratified ≈ naive (signal looks **more stable** across timing).
- Top strata by sample weight:
  - `most_ads_hour`=13: control 1.66% (2170), treatment 2.51% (45485), lift 0.85 pp
  - `most_ads_hour`=12: control 1.70% (2060), treatment 2.41% (45238), lift 0.71 pp
  - `most_ads_hour`=11: control 1.46% (2061), treatment 2.25% (44149), lift 0.79 pp
  - `most_ads_hour`=14: control 1.61% (1869), treatment 2.86% (43779), lift 1.25 pp
  - `most_ads_hour`=15: control 2.52% (1828), treatment 2.98% (42855), lift 0.47 pp

## Interpretation (Important)
- The full-dataset estimate is best treated as **directional** unless assignment/comparability is confirmed.
- The allocation pattern is consistent with a **holdout** (treatment-heavy) design; holdouts can be valid for incremental measurement if randomized and stable over time.
- See **Robustness** section: if stratified lift deviates materially from naive lift, prioritize time-based confounding risk.
