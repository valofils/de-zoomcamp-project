
    
    

with child as (
    select pickup_locationid as from_field
    from `food-security-pipeline`.`ny_taxi_staging`.`stg_yellow_tripdata`
    where pickup_locationid is not null
),

parent as (
    select locationid as to_field
    from `food-security-pipeline`.`ny_taxi_core`.`dim_zones`
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


