-- models/marts/experiments/fct_experiment_summary.sql
-- -----------------------------------------------------------
-- PURPOSE:
--   This fact table produces high-level A/B test metrics by test_group.
--   Each row represents one experiment arm (e.g., 'ad' vs 'psa') and
--   includes counts, conversion rate, and exposure stats.
--
--   This is the primary source for:
--     - Power BI / dashboard cards (conversion rate by group)
--     - Quick experiment readouts (e.g., "Ad group converted at X% vs Y%")
--     - Feeding downstream statistical analysis in Python.
-- -----------------------------------------------------------

with users as (
    -- Base user-level features for the experiment, including:
    --   user_id, test_group, converted, total_ads, most_ads_day/hour, etc.
    -- This model was defined in: int_experiment_features.sql
    select *
    from {{ ref('int_experiment_features') }}
),

agg as (
    select
          -- Grouping key: each row in this fact table is one test group
          -- (e.g., 'ad' treatment vs 'psa' control).
          test_group

        -- Total number of users in this group (sample size).
        -- Important for checking balance and statistical power.
        , count(*)                         as n_users

        -- Number of users who converted in this group.
        -- Because `converted` is 0/1, the sum = count of conversions.
        , sum(converted)                   as n_converted

        -- Conversion rate for this group:
        -- Cast to float so the average = proportion of users with converted = 1.
        -- Example: 0.023 means a 2.3% conversion rate.
        , avg(converted::float)            as conversion_rate

        -- Average number of ads served per user in this group.
        -- Helps check if one group received systematically more exposure
        -- than the other (which could bias interpretation).
        , avg(total_ads)                   as avg_total_ads

        -- Median ads served per user (50th percentile).
        -- More robust to outliers than the mean; shows the "typical" exposure.
        , percentile_cont(0.5) within group (order by total_ads) as median_total_ads

        -- Average "most frequent ad hour" per user.
        -- Rough indicator of whether one group saw ads at different times of day.
        , avg(most_ads_hour)               as avg_most_ads_hour

    from users
    group by test_group
)

-- Final output: one row per test group with summary metrics.
select *
from agg
;

-- BUSINESS CONTEXT:
-- This fact table provides a single source of truth for A/B test outcomes
-- at the group level. Stakeholders can quickly compare sample size, conversion
-- rate, and exposure between treatment and control when deciding whether to
-- roll out the ad variant or keep the PSA as the default.
-- By centralizing these metrics here, we ensure consistency across dashboards
-- and analyses, reducing confusion and speeding up decision-making.
-- Analysts and product managers can rely on this table for accurate,
-- up-to-date experiment summaries without needing to recalculate metrics
-- from raw user-level data each time.

