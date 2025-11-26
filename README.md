# Marketing A/B Test – Ad vs PSA (Kaggle)

## Executive Summary

- **Business impact:** Replacing PSA with a product Ad increases conversion from **1.79% to 2.55%** – a **+0.76 pp lift (~+42% relative)** that is statistically robust and practically meaningful at scale.
- **Experiment quality:** I validated **exposure** and **timing** balance using t-tests and chi-square tests, showing the uplift is unlikely to be driven by biased traffic.
- **What this shows about me:** I can **design, validate, and interpret** A/B tests end-to-end, package the logic into reusable code, and translate the results into decisions a product or marketing team can act on.

**Audience:** Product managers, marketing leads, and analytics teams deciding whether to roll out the Ad variant and where to focus future optimization.


End-to-end analysis of a marketing A/B test (Ad vs PSA) using the Kaggle `marketing_AB` dataset.

This project simulates how I’d own an experiment in a real team:

- Validate that the experiment is **well-designed and balanced**
- Quantify the **uplift** and **uncertainty** (effect size, p-values, CIs, power)
- Explore **for whom** the Ad works best via cohort analysis
- Package core logic into a small, reusable **Python module**
- (Planned) Build **Tableau dashboards** on top of the pipeline

---

## 1. Business Question

A product team is running an experiment:

> In a given ad slot, should we show a **product Ad** or a **public service announcement (PSA)** to maximize purchases?

- **Control:** PSA (no product ad in that slot)  
- **Treatment:** Product Ad  
- **Outcome:** `converted` – whether the user eventually bought

Key goals:

1. Is the experiment **trustworthy** (balanced exposure & timing)?
2. What is the **incremental lift** in conversion from showing the Ad?
3. How **precise** is that estimate (confidence interval, power)?
4. Are there **cohorts** (by exposure, day-of-week, etc.) where the Ad works better or worse?
5. What concrete **recommendations** should the business act on?

---

## 2. Key Results (TL;DR)

Using the Kaggle `marketing_AB` dataset:

- **Conversion rates**
  - PSA (control): **1.79%**
  - Ad (treatment): **2.55%**
- **Absolute lift:** **+0.76 percentage points** (2.55% − 1.79%)  
- **Relative lift:** ≈ **+42% uplift** vs PSA

**Statistical inference**

- Two-proportion z-test:
  - z ≈ **7.37**
  - p-value ≪ **0.001** (prints as `0.000000` at 6 decimals)
- 95% confidence interval for lift (Ad − PSA):
  - ≈ **[0.60, 0.94] percentage points**

**Interpretation**

> Showing the Ad instead of the PSA increases conversion by roughly **0.6–0.9 percentage points**, with a best estimate around **0.8 pp**.  
> This effect is **statistically robust** given the large sample size and is practically meaningful for a high-volume funnel.

### Why this matters to the business

To make the lift tangible, assume:

- **Monthly traffic through this slot:** 10,000,000 users
- **Average order value (AOV):** \$50

With PSA:

- Conversion ≈ **1.79%** → **179,000** orders

With Ad:

- Conversion ≈ **2.55%** → **255,000** orders

**Incremental impact from switching PSA → Ad:**

- **+76,000 additional orders per 10M users**
- At \$50 AOV, that’s ≈ **\$3.8M in additional revenue per 10M users** exposed

Even if we cut these assumptions in half, the Ad represents a **multi-million dollar lever** at scale. That’s why getting the experiment design, QC, and interpretation right actually matters.

**At scale (back-of-envelope)**

If 1,000,000 users see this slot:

- PSA would generate ~**17,900** conversions at 1.79%
- Ad would generate ~**25,500** conversions at 2.55%
- Incremental impact: ~**7,600 extra conversions per million users**

With an average profit of **$X** per conversion, that’s roughly **$7,600 × X** in incremental profit per million impressions.



**Experiment quality**

- **Exposure (`total_ads`)** is effectively balanced between groups:
  - Avg ads per user: Ad ≈ 24.82, PSA ≈ 24.76 (diff ≈ 0.06 ads, p ≈ 0.83)
- **Timing (`most_ads_day`, `most_ads_hour`)** shows small but not dramatic differences:
  - Day-of-week and hour-of-day distributions differ by at most a few percentage points
  - Statistically detectable (huge N), but **practically modest**

**Overall:**  
The experiment is **credible**, and the Ad delivers a **real, positive uplift** in conversion.

Cohort-level insights and recommendations are detailed in **Notebook 3**.

---

---

## 10. Visuals (Selected Charts)

### 1. Conversion rate by group

![Conversion rate by group](visuals/conversion_rate_by_group.png)

Overall conversion rates for **PSA vs Ad**.  
This makes the **+0.76 pp / +42% relative lift** immediately visible for stakeholders.

---

### 2. Conversion rate by day and test group

![Conversion rate by day and test group](visuals/conversion_rate_by_day_and_test_group.png)

Conversion rates by **day of week** split by **test_group** (Ad vs PSA).  
Highlights which days (e.g., early-week vs late-week) show the strongest incremental gains from running the Ad.

---

### 3. Conversion rate by ad-intensity cohort and group

![Conversion rate by ad intensity cohort and group](visuals/conversion_rate_by_ad_intensity_cohort_and_group.png)

Conversion rates by **ads_intensity_bucket** (light / medium / heavy exposure) and group.  
Shows how **exposure intensity interacts with creative** – where the Ad delivers the largest uplift and where returns start to flatten.


## 3. Tech Stack

- **Python / Jupyter**
  - `pandas`, `numpy`, `matplotlib`, `seaborn`
  - `statsmodels` (two-proportion z-tests, confidence intervals, power)
- **dbt (Data Build Tool)**
  - Staging, intermediate, and mart models for experiment features & cohorts
- **Custom Python module**
  - `src/ab_experiment/` for:
    - `get_experiment_df()` data access & cleaning
    - reusable stats helpers (conversion lift, z-test, CI)
- **(Planned) Tableau**
  - `tableau/` folder for experiment overview dashboards

---

## 4. Repository Structure

```text
.
├── data_raw/
│   └── marketing_AB.csv         # Kaggle marketing A/B dataset
├── dbt_marketing_ab/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   │       └── experiments/     # Cohorts, intensity buckets, etc.
│   └── ...                      # dbt project files
├── notebooks/
│   ├── 01_eda_and_randomization_checks.ipynb
│   ├── 02_ab_test_frequentist_and_power.ipynb
│   └── 03_cohort_heterogeneity_and_recommendations.ipynb
├── reports/
│   └── ab_experiment_summary.md # Optional 1-page summary for stakeholders
├── src/
│   └── ab_experiment/
│       ├── __init__.py
│       ├── data_access.py       # get_experiment_df()
│       └── stats.py             # compute_conversion_lift, z-tests, CIs, power
├── tableau/                     # (Planned) Tableau workbooks
│   └── README.md                # Placeholder / future description
├── visuals/                     # (Planned) Tableau workbooks
│   ├── conversion_rate_by_group.png
│   ├── conversion_rate_by_day_and_test_group.png
│   └── conversion_rate_by_ad_intensity_cohort_and_group.png
├── README.md
└── requirements.txt
```

---

## 5. Notebooks Overview

### `01_eda_and_randomization_checks.ipynb`

**Goal:** Validate that the experiment is well-designed and balanced before trusting any uplifts.

- Load & clean `marketing_AB.csv`
- Explore distributions:
  - Group sizes
  - `total_ads`
  - `most_ads_day`
  - `most_ads_hour`
- Check **exposure balance**:
  - Welch’s t-test on `total_ads` between Ad and PSA
- Check **timing balance**:
  - Chi-square tests on `most_ads_day × test_group`
  - Chi-square tests on `most_ads_hour × test_group`
- Summarize:
  - Exposure is essentially identical
  - Timing differences are small and manageable

---

### `02_ab_test_frequentist_and_power.ipynb`

**Goal:** Quantify uplift and uncertainty; test significance and power.

- Compute basic metrics:
  - Conversion per group
  - Absolute & relative lift
- Run **two-proportion z-test** (Ad vs PSA)
- Build **95% confidence interval** for the lift
- Run a basic **power analysis**:
  - Was the experiment well-powered for the observed effect?
  - How many users per group would we need to detect a smaller, business-relevant lift?

Includes both:

- A **high-level version** using `ab_experiment.stats` helpers  
- A **fully expanded version** with raw `statsmodels` code and comments (for transparency / learning)

---

### `03_cohort_heterogeneity_and_recommendations.ipynb`

**Goal:** Understand *for whom* the Ad works best and produce actionable recommendations.

- Cohort definitions (via dbt models), e.g.:
  - `ads_intensity_bucket` (light / medium / heavy exposure)
  - `most_ads_day` (day-of-week cohorts)
- For each cohort:
  - Compute conversion rates for Ad vs PSA
  - Estimate uplift & significance using the same stats helpers
- Translate into a **playbook**:
  - Where lift is strongest and volume is meaningful
  - Where performance is weaker or uncertain
  - Suggestions for targeting & experimentation follow-ups

---

## 6. The `ab_experiment` Python Module

To avoid copy-pasting logic across notebooks, core functionality is packaged in `src/ab_experiment/`.

### Data access

```python
from ab_experiment import get_experiment_df

df = get_experiment_df()  # loads and cleans marketing_AB.csv
```

### Stats helpers

```python
from ab_experiment import stats as ab_stats

lift = ab_stats.compute_conversion_lift(df)
# LiftResult with:
# - control_rate, treatment_rate
# - abs_lift, rel_lift
# - counts for each group

z_res = ab_stats.two_proportion_ztest(lift)
# {'z_stat': ..., 'p_value': ...}

ci = ab_stats.lift_confint(lift)
# {'ci_low': ..., 'ci_high': ...}
```

This mirrors how a production analytics codebase would encapsulate experiment logic in reusable functions instead of re-coding each test in notebooks.

---

## 7. How to Run Locally

1. **Clone the repo**

```bash
git clone <this-repo-url>.git
cd marketing-ab-experiment
```

2. **Create a virtual environment and install dependencies**

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scriptsactivate
pip install -r requirements.txt
```

3. **Launch Jupyter**

```bash
jupyter lab
# or
jupyter notebook
```

4. **Run notebooks in order**

- `01_eda_and_randomization_checks.ipynb`
- `02_ab_test_frequentist_and_power.ipynb`
- `03_cohort_heterogeneity_and_recommendations.ipynb`

---

## 8. What this project demonstrates about my skill set

This repo is designed to show how I would contribute as a Data Analyst / Analytics Engineer on a real team:

- **Experiment design & QC**
  - I don’t just compare two percentages — I first validate:
    - Group balance on exposure (`total_ads`)
    - Timing distributions (`most_ads_day`, `most_ads_hour`)
  - I treat randomization checks and experiment credibility as first-class steps before claiming uplift.

- **Statistical rigor with practical framing**
  - Use of two-proportion z-tests, confidence intervals, and power analysis to:
    - Quantify *how big* the effect is,
    - Assess *how certain* we are,
    - Communicate both in plain language (percentage-point lift, approximate revenue impact).

- **Analytics engineering mindset**
  - Factored common logic into a small Python package (`src/ab_experiment`) instead of copy-pasting code across notebooks.
  - Structured dbt models into staging → intermediate → marts, mirroring modern analytics stacks.
  - This makes it easy to reuse the same QC + inference patterns for future experiments.

- **Data storytelling & stakeholder-oriented outputs**
  - Notebooks are organized around stakeholder questions:
    - “Is this experiment trustworthy?”
    - “Did the Ad work, by how much, and how confident are we?”
    - “For which users does it work best, and what should we do next?”
  - The final outputs (notebooks + README) are written as something I could hand to a PM or marketing lead, not just another course assignment.


## 9. Roadmap / Future Work

Planned enhancements:

- **Tableau dashboards**
  - Build a high-level “Experiment Overview” dashboard (conversion, lift, confidence intervals, cohorts).
  - Add drill-downs by exposure intensity and day-of-week.
- **Logistic regression / causal modeling**
  - Model `converted ~ test_group + total_ads + most_ads_day_index` to control for covariates.
- **Automation**
  - Wire dbt models + Python analysis into a scheduled pipeline.
  - Parameterize the `ab_experiment` module so it can be reused for other tests.

This repo is intentionally structured so it can grow from a **single experiment analysis** into a more general **A/B testing and reporting pipeline** with BI dashboards on top.
