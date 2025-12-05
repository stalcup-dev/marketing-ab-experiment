# Experiment Integrity Report
## SRM (Allocation Diagnostics)
### 50/50 reference (classic A/B)
- Observed: {'ad': 564577, 'psa': 23524}
- Expected (counts): {'ad': 294050.5, 'psa': 294050.5}
- p-value: <1e-300
- Status: FAIL

### 96/4 reference (holdout-style)
- Observed: {'ad': 564577, 'psa': 23524}
- Expected (counts): {'ad': 564577.0, 'psa': 23524.0}
- p-value: 0.999788
- Status: PASS

**Interpretation:** Failing 50/50 but passing 96/4 is consistent with a treatment-heavy holdout design rather than a balanced randomized 50/50 experiment.

## Data Quality
- Rows: 588101
- Groups: {'ad': 564577, 'psa': 23524}
- Converted values: {0: 573258, 1: 14843}
- Duplicate user_ids: 0

_Cramér's V thresholds are rule-of-thumb guidelines._

## Balance / Distribution: most_ads_day
- p-value: 4.84907e-48

- effect_size (Cramér's V): 0.020 (negligible)

## Balance / Distribution: most_ads_hour
- p-value: 1.09457e-28

- effect_size (Cramér's V): 0.018 (negligible)

