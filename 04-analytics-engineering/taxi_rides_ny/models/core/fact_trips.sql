{{
  config(
    materialized='table',
    partition_by={
      "field": "pickup_datetime",
      "data_type": "timestamp",
      "granularity": "month"
    },
    cluster_by=["vendorid", "payment_type"]
  )
}}

with yellow_trips as (

    select *,
        'Yellow' as taxi_type
    from {{ ref('stg_yellow_tripdata') }}

),

dim_zones_pickup as (

    select * from {{ ref('dim_zones') }}

),

dim_zones_dropoff as (

    select * from {{ ref('dim_zones') }}

)

select
    -- trip identifiers
    yellow_trips.tripid,
    yellow_trips.vendorid,
    yellow_trips.taxi_type,
    yellow_trips.ratecodeid,

    -- timestamps
    yellow_trips.pickup_datetime,
    yellow_trips.dropoff_datetime,

    -- calculated duration
    timestamp_diff(yellow_trips.dropoff_datetime, yellow_trips.pickup_datetime, minute) as trip_duration_minutes,

    -- pickup location
    yellow_trips.pickup_locationid,
    pickup_zone.borough                         as pickup_borough,
    pickup_zone.zone                            as pickup_zone,
    pickup_zone.service_zone                    as pickup_service_zone,

    -- dropoff location
    yellow_trips.dropoff_locationid,
    dropoff_zone.borough                        as dropoff_borough,
    dropoff_zone.zone                           as dropoff_zone,
    dropoff_zone.service_zone                   as dropoff_service_zone,

    -- trip info
    yellow_trips.store_and_fwd_flag,
    yellow_trips.passenger_count,
    yellow_trips.trip_distance,
    yellow_trips.trip_type,

    -- payment
    yellow_trips.payment_type,
    yellow_trips.payment_type_description,
    yellow_trips.fare_amount,
    yellow_trips.extra,
    yellow_trips.mta_tax,
    yellow_trips.tip_amount,
    yellow_trips.tolls_amount,
    yellow_trips.improvement_surcharge,
    yellow_trips.congestion_surcharge,
    yellow_trips.airport_fee,
    yellow_trips.total_amount,

    -- derived: tip percentage
    case
        when yellow_trips.fare_amount > 0
        then round(yellow_trips.tip_amount / yellow_trips.fare_amount * 100, 2)
        else 0
    end as tip_pct

from yellow_trips

inner join dim_zones_pickup  as pickup_zone
    on yellow_trips.pickup_locationid  = pickup_zone.locationid

inner join dim_zones_dropoff as dropoff_zone
    on yellow_trips.dropoff_locationid = dropoff_zone.locationid

-- Filter out data quality issues
where yellow_trips.trip_distance > 0
  and yellow_trips.fare_amount   > 0
  and yellow_trips.passenger_count > 0
