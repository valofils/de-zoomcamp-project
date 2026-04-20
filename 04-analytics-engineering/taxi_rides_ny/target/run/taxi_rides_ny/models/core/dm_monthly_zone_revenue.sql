
  
    

    create or replace table `food-security-pipeline`.`ny_taxi_core`.`dm_monthly_zone_revenue`
      
    
    

    OPTIONS()
    as (
      

-- Data mart: monthly revenue and trip stats by pickup zone
-- Useful for dashboards and reporting

with fact as (
    select * from `food-security-pipeline`.`ny_taxi_core`.`fact_trips`
),

monthly as (

    select
        date_trunc(pickup_datetime, month)  as revenue_month,
        taxi_type,
        pickup_locationid,
        pickup_borough,
        pickup_zone,
        pickup_service_zone,

        -- trip volume
        count(*)                             as total_trips,
        sum(passenger_count)                 as total_passengers,
        sum(trip_distance)                   as total_distance_miles,
        avg(trip_distance)                   as avg_distance_miles,

        -- duration
        avg(trip_duration_minutes)           as avg_duration_minutes,

        -- revenue
        sum(fare_amount)                     as total_fare,
        sum(tip_amount)                      as total_tips,
        sum(tolls_amount)                    as total_tolls,
        sum(total_amount)                    as total_revenue,
        avg(total_amount)                    as avg_revenue_per_trip,
        avg(tip_pct)                         as avg_tip_pct,

        -- payment mix
        countif(payment_type = 1)            as credit_card_trips,
        countif(payment_type = 2)            as cash_trips

    from fact
    group by 1, 2, 3, 4, 5, 6

)

select * from monthly
order by revenue_month, total_revenue desc
    );
  