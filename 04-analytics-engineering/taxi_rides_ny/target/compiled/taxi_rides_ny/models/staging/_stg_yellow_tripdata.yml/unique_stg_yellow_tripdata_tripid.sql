
    
    

with dbt_test__target as (

  select tripid as unique_field
  from `food-security-pipeline`.`ny_taxi_staging`.`stg_yellow_tripdata`
  where tripid is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


