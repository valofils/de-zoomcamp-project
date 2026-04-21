-- stg_ipc_phases.sql
-- Subnational IPC phase classifications from FEWS NET FDW.
-- One row per area / reporting period / scenario.
-- Contains phase 1-5 area-level classifications (no population estimates).

with source as (
    select * from {{ source('fewsnet_raw', 'ipc_phases') }}
),

renamed as (
    select
        upper(trim(country_code))            as country_code,
        trim(geographic_unit_name)           as area_name,
        trim(fnid)                           as area_id,
        projection_start                     as period_date,
        extract(year from projection_start)  as period_year,
        cast(value as INT64)                 as ipc_phase,
        upper(trim(scenario))                as scenario,
        created                              as created_at
    from source
    where
        country_code is not null
        and projection_start is not null
        and value between 1 and 5
        and scenario in ('CS', 'ML1', 'ML2', 'ML')
)

select * from renamed
