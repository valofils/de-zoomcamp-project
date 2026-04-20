
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        vendorid as value_field,
        count(*) as n_records

    from `food-security-pipeline`.`ny_taxi_staging`.`stg_yellow_tripdata`
    group by vendorid

)

select *
from all_values
where value_field not in (
    1,2
)



  
  
      
    ) dbt_internal_test