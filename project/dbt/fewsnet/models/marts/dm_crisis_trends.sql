-- dm_crisis_trends.sql
-- Annual Phase 3+ population trend per country, Current Situation only.
-- Powers the temporal trend tile in the Looker Studio dashboard.

with fct as (
    select * from {{ ref('fct_food_insecurity') }}
    where scenario = 'CS'
),

-- Use latest period per year per country to avoid double-counting
-- (FEWS NET publishes ~3 reports per year)
latest_per_year as (
    select
        country_code,
        country_name,
        sub_region,
        period_year,
        max(period_date) as latest_period_date
    from fct
    group by 1, 2, 3, 4
),

joined as (
    select
        l.country_code,
        l.country_name,
        l.sub_region,
        l.period_year,
        l.latest_period_date,
        f.pop_phase3plus,
        f.pop_phase3plus_low,
        f.pop_phase3plus_high
    from latest_per_year l
    inner join fct f
        on  f.country_code = l.country_code
        and f.period_date  = l.latest_period_date
)

select * from joined
order by country_code, period_year
