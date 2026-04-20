
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        borough as value_field,
        count(*) as n_records

    from `food-security-pipeline`.`ny_taxi_core`.`dim_zones`
    group by borough

)

select *
from all_values
where value_field not in (
    'Manhattan','Queens','Brooklyn','Bronx','Staten Island','EWR','Unknown'
)



  
  
      
    ) dbt_internal_test