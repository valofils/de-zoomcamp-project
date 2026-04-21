-- Fails if any row has a negative Phase 3+ population estimate.
select
    country_code,
    period_date,
    scenario,
    pop_phase3plus
from {{ ref('fct_food_insecurity') }}
where pop_phase3plus < 0
