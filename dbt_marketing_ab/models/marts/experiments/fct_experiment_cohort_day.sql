-- models/marts/experiments/fct_experiment_cohort_day.sql
-- -----------------------------------------------------------
-- PURPOSE:
--   This fact table summarizes experiment outcomes by:
--     - most_ads_day (day of week when each user saw the most ads)
--     - test_group   (ad vs psa)
--
--   Each row represents a day-of-week + test group cohort with:
--     - user counts
--     - conversion counts
--     - conversion rate
--
--   This enables analysis of how the experiment performed across
--   different days of the week (behavioral cohorts), rather than
--   only at the overall test-group level.
-- -----------------------------------------------------------

with users as (
    -- Base user-level dataset with engineered features such as:
    --   most_ads_day, most_ads_day_index, ads_intensity_bucket, etc.
    -- Comes from: int_experiment_features.sql
    select *
    from {{ ref('int_experiment_features') }}
),

agg as (
    select
          -- Day of week when this user saw the most ads.
          -- This defines our "day cohort".
          most_ads_day

        -- Numeric index for calendar ordering:
        -- Monday = 1, ..., Sunday = 7
        -- Useful for sorting and plotting in correct day order.
        , most_ads_day_index

        -- Experiment arm: 'ad' (treatment) vs 'psa' (control).
        , test_group

        -- Number of users in this day + test_group cohort.
        , count(*)                       as n_users

        -- Number of converters in this cohort.
        -- Sum over a 0/1 flag gives the count of conversions.
        , sum(converted)                 as n_converted

        -- Conversion rate in this cohort:
        -- mean of 0/1 indicator = probability of conversion.
        , avg(converted::float)          as conversion_rate

    from users
    group by most_ads_day, most_ads_day_index, test_group
)

-- Final output: one row per (day-of-week, test_group) cohort.
select *
from agg
order by most_ads_day_index, test_group
;

-- BUSINESS CONTEXT:
-- This table reveals how the A/B test performs across different days of the week.
-- Marketing and growth teams can use it to:
--   - Identify which days show the strongest lift for the ad vs the PSA.
--   - Prioritize ad spend or campaign launches on high-performing days.
--   - Spot days where the treatment underperforms control and investigate why.
--
-- In dashboards, this fact table powers charts like:
--   "Conversion rate by day-of-week and test group",
-- allowing stakeholders to optimize campaign scheduling, pacing, and budget
-- allocation based on when users are most responsive.
