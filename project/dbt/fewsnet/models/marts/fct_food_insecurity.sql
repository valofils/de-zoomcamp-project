-- fct_food_insecurity.sql
-- Core fact table: Phase 3+ population estimates per country / period / scenario.
-- Source: ipc_population endpoint (which provides 3+ aggregate totals only).

with pop as (
    select * from {{ ref('stg_ipc_population') }}
),

countries as (
    select * from {{ ref('dim_countries') }}
),

joined as (
    select
        {{ dbt_utils.generate_surrogate_key(
            ['pop.country_code', 'pop.period_date', 'pop.scenario']
        ) }}                                as record_id,

        pop.country_code,
        coalesce(c.country_name, pop.country_name_raw) as country_name,
        c.sub_region,
        pop.period_date,
        pop.period_year,
        pop.period_month,
        pop.phase_label,
        pop.scenario,
        pop.population_estimate             as pop_phase3plus,
        pop.population_low                  as pop_phase3plus_low,
        pop.population_high                 as pop_phase3plus_high,
        pop.created_at

    from pop
    left join countries c using (country_code)
)

select * from joined
