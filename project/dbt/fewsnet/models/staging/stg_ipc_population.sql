-- stg_ipc_population.sql
-- IPC Phase 3+ population aggregates from FEWS NET FDW.
-- This endpoint only returns 3+ aggregate rows (not phase 1-5 breakdowns).
-- Scenario codes: CS (current), ML (near-term projection), PN (previous)

with source as (
    select * from {{ source('fewsnet_raw', 'ipc_population') }}
),

renamed as (
    select
        upper(trim(country_code))            as country_code,
        upper(trim(country))                 as country_name_raw,
        projection_start                     as period_date,
        extract(year from projection_start)  as period_year,
        extract(month from projection_start) as period_month,
        trim(phase)                          as phase_label,
        upper(trim(scenario))                as scenario,
        cast(value as INT64)                 as population_estimate,
        cast(low_value as INT64)             as population_low,
        cast(high_value as INT64)            as population_high,
        created                              as created_at
    from source
    where
        country_code is not null
        and projection_start is not null
        and value is not null
        and scenario in ('CS', 'ML', 'PN')
)

select * from renamed
