-- Fails if any country has no data after 2019 (would indicate ingestion gap).
select
    country_code,
    max(period_year) as latest_year
from {{ ref('dm_crisis_trends') }}
group by 1
having max(period_year) < 2020
