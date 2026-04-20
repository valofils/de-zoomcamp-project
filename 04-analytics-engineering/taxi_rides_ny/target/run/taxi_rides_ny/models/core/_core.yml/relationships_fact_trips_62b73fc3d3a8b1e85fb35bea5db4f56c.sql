
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select dropoff_locationid as from_field
    from `food-security-pipeline`.`ny_taxi_core`.`fact_trips`
    where dropoff_locationid is not null
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



  
  
      
    ) dbt_internal_test