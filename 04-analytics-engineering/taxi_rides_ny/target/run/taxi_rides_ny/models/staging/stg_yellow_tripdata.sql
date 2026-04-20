

  create or replace view `food-security-pipeline`.`ny_taxi_staging`.`stg_yellow_tripdata`
  OPTIONS()
  as 

with source as (

    select * from `food-security-pipeline`.`ny_taxi`.`yellow_tripdata`

),

renamed as (

    select
        -- identifiers
        to_hex(md5(cast(coalesce(cast(VendorID as string), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(tpep_pickup_datetime as string), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(tpep_dropoff_datetime as string), '_dbt_utils_surrogate_key_null_') as string))) as tripid,
        cast(VendorID as integer)                   as vendorid,
        cast(RatecodeID as integer)                 as ratecodeid,
        cast(PULocationID as integer)               as pickup_locationid,
        cast(DOLocationID as integer)               as dropoff_locationid,

        -- timestamps
        cast(tpep_pickup_datetime as timestamp)     as pickup_datetime,
        cast(tpep_dropoff_datetime as timestamp)    as dropoff_datetime,

        -- trip info
        store_and_fwd_flag,
        cast(passenger_count as integer)            as passenger_count,
        cast(trip_distance as numeric)              as trip_distance,
        1 as trip_type, -- yellow = 1, green = 2

        -- payment info
        cast(payment_type as integer)               as payment_type,
        

    case cast(payment_type as integer)
        when 1 then 'Credit card'
        when 2 then 'Cash'
        when 3 then 'No charge'
        when 4 then 'Dispute'
        when 5 then 'Unknown'
        when 6 then 'Voided trip'
        else 'EMPTY'
    end

 as payment_type_description,

        -- amounts
        cast(fare_amount as numeric)                as fare_amount,
        cast(extra as numeric)                      as extra,
        cast(mta_tax as numeric)                    as mta_tax,
        cast(tip_amount as numeric)                 as tip_amount,
        cast(tolls_amount as numeric)               as tolls_amount,
        cast(improvement_surcharge as numeric)      as improvement_surcharge,
        cast(total_amount as numeric)               as total_amount,
        coalesce(cast(congestion_surcharge as numeric), 0) as congestion_surcharge,
        coalesce(cast(Airport_fee as numeric), 0)   as airport_fee

    from source

    where tpep_pickup_datetime >= '2024-01-01'
      and tpep_pickup_datetime <  '2024-07-01'

)

select * from renamed

;

