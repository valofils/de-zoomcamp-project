
  
    

    create or replace table `food-security-pipeline`.`ny_taxi_core`.`dim_zones`
      
    
    

    OPTIONS()
    as (
      

select
    cast(locationid as integer)  as locationid,
    borough,
    zone,
    replace(service_zone, 'Boro', 'Green') as service_zone

from `food-security-pipeline`.`ny_taxi`.`taxi_zone_lookup`
    );
  