# Experiment Design Spec — Ads vs PSA (Marketing AB)

## 1) Decision & Hypothesis
**Decision:** Should we show Ads instead of PSAs to increase conversions?

**Primary hypothesis (H1):** Ads increase conversion rate vs PSA.  
**Null (H0):** No difference in conversion rate.

## 2) Unit of Randomization / Assignment
**Unit:** user_id (one assignment per user).  
**Assignment mechanism (recommended):** deterministic hash/bucket (e.g., stable user hash mod 100).  
**Target split:** 50/50 unless there’s a deliberate holdout design.

**Note:** This dataset appears treatment-heavy (~96/4). If this is an intentional holdout, we must document the business rationale and the exact intended split and keep it stable.

## 3) Metrics
### Primary metric (North Star)
- **Conversion rate:** converted / users (define conversion event precisely)

### Guardrails (must not regress)
- Bounce rate / session quality proxy
- Revenue per user (if monetized)
- Unsubscribes/complaints (if applicable)
- Performance (page load time / latency)

## 4) Eligibility & Exposure
- Define who is eligible (new users only? all users? geo/device filters?)
- Define exposure rules (first exposure only vs repeated exposures)
- Define analysis window (same-session vs 7-day conversion)

## 5) Instrumentation / Logging Requirements
Required fields per event/user:
- user_id (stable)
- assigned_group (ad vs psa)
- timestamp (UTC)
- conversion event + timestamp
- key pre-treatment covariates if available: traffic source, campaign, device, geo

## 6) Integrity Checks (automated gates)
### Allocation / SRM
- SRM check vs intended split (alpha = 0.01)
- Monitor allocation daily; alert on drift

### Data quality
- Missingness checks on keys (group, converted, user_id)
- Duplicate user_id rate
- Range checks (converted ∈ {0,1})

### Comparability checks (pre-treatment)
- Balance checks on true pre-treatment covariates (device/source/geo/campaign)
- If only timing proxies exist (day/hour), treat as diagnostics—not proof of randomization

## 7) Sample Size / Power / MDE
Inputs:
- Baseline conversion rate (p0): ___
- Minimum detectable effect (absolute, pp): ___
- Alpha: 0.05
- Power: 0.80

Outputs:
- Required sample size per group: ___
- Planned duration: ___ days

**Note:** If running a holdout (e.g., 96/4), power will be driven primarily by the small holdout group—plan accordingly.

## 8) Stopping Rule (avoid peeking bias)
Choose ONE:
- **Fixed-horizon:** run until planned sample size is reached; analyze once.
- **Sequential:** pre-register an alpha-spending plan (only if the org supports it).

No ad-hoc early stopping based on interim p-values.

## 9) Analysis Plan (pre-registered)
Primary:
- Difference in proportions (ad - psa) + 95% CI
- Two-proportion z-test (or equivalent)

Robustness:
- Stratified pooled lift by day/hour (diagnostic)
- If pre-treatment covariates exist: regression-adjusted estimate controlling for source/device/geo

Multiple comparisons:
- Primary metric unadjusted; adjust only secondary metrics if many are tested.

## 10) Decision Rule
Ship / roll out if:
- CI lower bound > 0 **and**
- Guardrails acceptable **and**
- Integrity gates pass (SRM/QA stable)

Do not ship if:
- SRM fails against intended split (unexplained)
- Key covariate imbalance suggests non-comparability
- Lift disappears under robustness checks (suggestive of confounding)

## 11) Monitoring After Launch
- Continue tracking conversion rate, guardrails, and segments
- Monitor for novelty effects and regression to mean over time
- Add holdout / shadow testing for long-term incrementality if needed
