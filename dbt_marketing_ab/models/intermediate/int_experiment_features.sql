-- models/intermediate/int_experiment_features.sql
-- ------------------------------------------------------
-- PURPOSE:
-- This intermediate dbt model:
--   - Starts from the cleaned staging model `stg_marketing_ab`
--   - Adds feature engineering for cohort and segment analysis:
--       * numeric weekday index
--       * ad intensity buckets
--       * time-of-day buckets
--   - Produces a richer user-level table for A/B and cohort analysis.
-- This will answer:
-- “For which users did this experiment work best, and how should we act on that?”

-- ------------------------------------------------------

with base as (
    -- Pull all columns from the staging model.
    -- {{ ref('stg_marketing_ab') }} tells dbt:
    --   "Use the model named `stg_marketing_ab`"
    -- which resolves to the table/view dbt created earlier.
    select *
    from {{ ref('stg_marketing_ab') }}
),

with_features as (
    select
          -- Core fields passed through from staging
          user_id
        , test_group
        , converted
        , total_ads
        , most_ads_day
        , most_ads_hour

        -- --------------------------------------------------
        -- FEATURE 1: numeric weekday index for ordering
        -- Turn 'Monday'...'Sunday' into 1...7 so:
        --   - we can order days logically
        --   - we can optionally use it as an ordinal variable
        -- --------------------------------------------------
        , case most_ads_day
            when 'Monday'    then 1
            when 'Tuesday'   then 2
            when 'Wednesday' then 3
            when 'Thursday'  then 4
            when 'Friday'    then 5
            when 'Saturday'  then 6
            when 'Sunday'    then 7
          end as most_ads_day_index

        -- --------------------------------------------------
        -- FEATURE 2: ad intensity buckets for cohorts
        -- Group users by how many total ads they saw:
        --   low    →  1–4  ads
        --   medium →  5–30 ads
        --   high   → >30   ads
        --
        -- This enables analysis like:
        --   "Does treatment effect differ by exposure level?"
        -- --------------------------------------------------
        , case
            when total_ads < 5                  then 'low (1-4)'
            when total_ads between 5 and 30     then 'medium (5-30)'
            else 'high (>30)'
          end as ads_intensity_bucket

        -- --------------------------------------------------
        -- FEATURE 3: time-of-day buckets for cohorts
        -- Convert hour-of-day (0–23) into semantic time blocks:
        --   night     → 0–5
        --   morning   → 6–11
        --   afternoon → 12–17
        --   evening   → 18–23
        --
        -- This lets you ask:
        --   "Are evening users more responsive to ads than morning users?"
        -- --------------------------------------------------
        , case
            when most_ads_hour between 0 and 5   then 'night (0-5)'
            when most_ads_hour between 6 and 11  then 'morning (6-11)'
            when most_ads_hour between 12 and 17 then 'afternoon (12-17)'
            else 'evening (18-23)'
          end as ads_hour_bucket

    from base
)

-- Final output: full feature-enhanced table.
select *
from with_features;
