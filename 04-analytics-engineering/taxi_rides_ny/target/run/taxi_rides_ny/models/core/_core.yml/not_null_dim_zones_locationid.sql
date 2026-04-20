
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select locationid
from `food-security-pipeline`.`ny_taxi_core`.`dim_zones`
where locationid is null



  
  
      
    ) dbt_internal_test