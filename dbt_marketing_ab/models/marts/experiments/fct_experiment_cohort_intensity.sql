-- models/marts/experiments/fct_experiment_cohort_intensity.sql
-- -----------------------------------------------------------
-- PURPOSE:
--   This fact table summarizes experiment performance by:
--     - ads_intensity_bucket (low / medium / high exposure)
--     - test_group          (ad vs psa)
--
--   Each row represents a cohort of users grouped by how many
--   ads they saw and which experiment arm they were in.
--   Metrics include:
--     - user count
--     - conversion count
--     - conversion rate
--     - average total ads
--
--   This enables analysis of whether the treatment effect
--   differs across exposure levels (heterogeneous treatment
--   effects by intensity cohort).
-- -----------------------------------------------------------

with users as (
    -- Base user-level features with engineered fields such as:
    --   ads_intensity_bucket, ads_hour_bucket, most_ads_day_index, etc.
    -- Comes from: int_experiment_features.sql
    select *
    from {{ ref('int_experiment_features') }}
),

agg as (
    select
          -- Cohort: users bucketed by how many total ads they saw.
        , ads_intensity_bucket

          -- Experiment arm: 'ad' (treatment) or 'psa' (control).
        , test_group

          -- Number of users in this (intensity_bucket, test_group) cohort.
        , count(*)                       as n_users

          -- Number of converters in this cohort.
          -- Sum over a 0/1 flag gives conversion count.
        , sum(converted)                 as n_converted

          -- Conversion rate in this cohort.
          -- Average of a 0/1 indicator = probability of conversion.
        , avg(converted::float)          as conversion_rate

          -- Average number of ads seen by users in this cohort.
          -- Useful to sanity-check that cohorts behave as intended
          -- and to see whether higher-intensity cohorts truly
          -- receive more impressions.
        , avg(total_ads)                 as avg_total_ads

    from users
    group by ads_intensity_bucket, test_group
)

-- Final output: one row per (ads_intensity_bucket, test_group) cohort.
select *
from agg
order by ads_intensity_bucket, test_group
;

-- BUSINESS CONTEXT:
-- This table shows how the A/B test performs across different levels
-- of ad exposure. It helps answer questions like:
--   - "Does the ad version outperform the PSA more strongly among
--      high-exposure users than low-exposure users?"
--   - "Is there a point of diminishing returns where additional ads
--      no longer increase conversion meaningfully?"
--
-- Marketing and growth teams can use these cohorts to:
--   - Tailor bidding and frequency caps by intensity bucket
--     (e.g., bid more aggressively for medium/high-exposure users
--      where the treatment drives incremental lift).
--   - Avoid overspending on segments where treatment and control
--     perform similarly (little or no incremental lift).
--   - Design follow-up experiments focused on the most responsive
--     exposure ranges.
--
-- In dashboards, this fact table powers visuals like:
--   "Conversion rate by intensity bucket and test group"
-- which directly supports optimization of spend, frequency, and
-- creative strategy based on how users respond at different
-- ad exposure levels.
