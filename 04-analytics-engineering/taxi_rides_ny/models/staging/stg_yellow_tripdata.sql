{{
  config(
    materialized='view'
  )
}}

with source as (

    select * from {{ source('staging', 'yellow_tripdata') }}

),

renamed as (

    select
        -- identifiers
        {{ dbt_utils.generate_surrogate_key(['VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']) }} as tripid,
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
        {{ get_payment_type_description('payment_type') }} as payment_type_description,

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

{% if is_incremental() %}
  where pickup_datetime > (select max(pickup_datetime) from {{ this }})
{% endif %}
