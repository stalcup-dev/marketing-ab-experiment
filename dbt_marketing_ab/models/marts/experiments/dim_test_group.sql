-- models/marts/experiments/dim_test_group.sql
-- -----------------------------------------------------------
-- PURPOSE:
--   This is a dimension table for experiment test groups.
--   It:
--     - Lists each unique test_group value (ad, psa)
--     - Adds a human-readable description for each group
--   This is useful for:
--     - Consistent labels in dashboards
--     - Joining onto fact tables for better readability
-- -----------------------------------------------------------
-- BUSINESS CONTEXT:
-- Centralizing test group labels here ensures every experiment report uses the same
-- control/treatment definitions, reducing confusion and making A/B results easier
-- to compare and act on across teams.
-- This dim table is the single source of truth for experiment group labels, allowing
-- marketing, product, and analytics teams to reuse the same control/treatment
-- definitions across multiple dashboards and A/B test readouts.


select distinct
    -- The raw categorical value from the staging model
    test_group,

    -- A human-friendly description for each test group.
    -- This keeps logic centralized: instead of hardcoding
    -- 'ad' vs 'psa' descriptions in every dashboard or query,
    -- you define it once here, and then join to this dimension.
    case
        when test_group = 'ad'  then 'Ad exposure'
        when test_group = 'psa' then 'Public Service Announcement (control)'
        -- You could add an ELSE here to catch unexpected values,
        -- but we already enforce accepted_values(['ad','psa']) in tests.
    end as test_group_description

from {{ ref('stg_marketing_ab') }}   -- Pulls from the cleaned staging model

-- distinct ensures one row per unique test_group,
-- so this dimension table will have exactly two rows: 'ad' and 'psa'.
;
