-- models/staging/stg_marketing_ab.sql
-- --------------------------------------------------------------
-- PURPOSE OF THIS MODEL:
-- This is a dbt *staging model* that:
--   1. Reads raw CSV data loaded into Postgres (`raw.marketing_ab`)
--   2. Cleans column names
--   3. Casts all data to proper types
--   4. Standardizes values ('True' → 1)
--   5. Prepares a clean, analytics-ready table
--
-- dbt best practice: staging models = 1:1 with raw sources.
-- --------------------------------------------------------------


-- STEP 1: Pull raw data from the source() macro
-- {{ source('raw', 'marketing_ab') }} points to the table defined in `sources.yml`.
-- It resolves to: raw.marketing_ab
with source as (
    select
          -- These column names have spaces and mixed casing.
          -- We SELECT them as-is from the raw CSV-loaded table...
          "user id"        as user_id_raw
        , "test group"     as test_group_raw
        , converted        as converted_raw
        , "total ads"      as total_ads_raw
        , "most ads day"   as most_ads_day_raw
        , "most ads hour"  as most_ads_hour_raw
    from {{ source('raw', 'marketing_ab') }}
),


-- STEP 2: Clean + cast + standardize fields
-- This is where we:
--   - Rename to snake_case
--   - Normalize values (e.g., make test groups lowercase)
--   - Cast numbers that were imported as strings
--   - Convert booleans into 0/1 integers
cleaned as (
    select
          -- Convert user_id to bigint — good for large IDs
          cast(user_id_raw as bigint) as user_id

        -- Lowercase test group values to ensure consistency: 'ad' or 'psa'
        , lower(test_group_raw)       as test_group

        -- Convert converted_raw (string boolean) into integer 0/1
        -- This handles:
        --   'True', 'true', '1'  → 1
        --   everything else → 0
        , case
            when converted_raw in ('True', 'true', '1') then 1
            else 0
          end                       as converted

        -- Convert ads to integer; CSV imports often treat numbers as text
        , cast(total_ads_raw as integer)  as total_ads

        -- `most_ads_day` already clean text (‘Monday’, etc.)
        , most_ads_day_raw               as most_ads_day

        -- Convert hour-of-day into integer (0–23)
        , cast(most_ads_hour_raw as integer) as most_ads_hour
    from source
)


-- STEP 3: Output the cleaned table
-- Final select of the cleaned CTE.
-- dbt creates a materialized table/view at: analytics.stg_marketing_ab
select *
from cleaned;
