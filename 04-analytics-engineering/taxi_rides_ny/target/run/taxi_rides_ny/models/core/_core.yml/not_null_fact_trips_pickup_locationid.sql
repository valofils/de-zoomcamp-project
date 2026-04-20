
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select pickup_locationid
from `food-security-pipeline`.`ny_taxi_core`.`fact_trips`
where pickup_locationid is null



  
  
      
    ) dbt_internal_test