
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select borough
from `food-security-pipeline`.`ny_taxi_core`.`dim_zones`
where borough is null



  
  
      
    ) dbt_internal_test