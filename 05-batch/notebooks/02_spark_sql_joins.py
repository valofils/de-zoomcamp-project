"""
Module 5 — Batch Processing with Apache Spark
Script 02: Spark SQL & Joins

Topics:
- Spark SQL (createOrReplaceTempView, spark.sql())
- DataFrame joins (inner, left, broadcast)
- GroupBy + aggregations
- Homework Q3: longest trip duration on Oct 15
- Homework Q4: least frequent pickup zone
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# ── 0. Paths ──────────────────────────────────────────────────────────────────
BASE_DIR   = "/workspaces/de-zoomcamp-project/05-batch"
TAXI_PATH  = f"{BASE_DIR}/data/yellow_tripdata_2024-10.parquet"
ZONES_PATH = f"{BASE_DIR}/data/taxi_zone_lookup.csv"

# ── 1. SparkSession ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 1 — SparkSession")
print("="*60)

spark = SparkSession.builder \
    .master("local[*]") \
    .appName("dezoomcamp-module5-sql-joins") \
    .config("spark.api.mode", "classic") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
print(f"Spark version : {spark.version}")

# ── 2. Load data ──────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 2 — Load taxi + zone data")
print("="*60)

df_taxi = spark.read.parquet(TAXI_PATH)

df_zones = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(ZONES_PATH)

print(f"Taxi rows     : {df_taxi.count():,}")
print(f"Zone rows     : {df_zones.count():,}")

print("\nZone schema:")
df_zones.printSchema()
df_zones.show(5)

# ── 3. Spark SQL basics ───────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 3 — Spark SQL")
print("="*60)

# Register DataFrames as temp views — SQL can query them by name
df_taxi.createOrReplaceTempView("taxi")
df_zones.createOrReplaceTempView("zones")

# Same as df_taxi.count() but via SQL
result = spark.sql("SELECT COUNT(*) AS total_trips FROM taxi")
result.show()

# Trips by vendor using SQL
spark.sql("""
    SELECT VendorID,
           COUNT(*)                        AS trips,
           ROUND(AVG(fare_amount), 2)      AS avg_fare,
           ROUND(AVG(trip_distance), 2)    AS avg_distance
    FROM   taxi
    GROUP  BY VendorID
    ORDER  BY VendorID
""").show()

# ── 4. Homework Q3 — Longest trip on October 15 ───────────────────────────────
print("\n" + "="*60)
print("HOMEWORK Q3 — Longest trip duration on Oct 15")
print("="*60)

# DataFrame API approach
longest_df = df_taxi \
    .withColumn("trip_duration_hours",
        F.round(
            (F.unix_timestamp("tpep_dropoff_datetime") -
             F.unix_timestamp("tpep_pickup_datetime")) / 3600, 2
        )) \
    .filter(
        F.to_date(F.col("tpep_pickup_datetime")) == F.lit("2024-10-15")
    ) \
    .select("tpep_pickup_datetime", "tpep_dropoff_datetime",
            "trip_distance", "trip_duration_hours") \
    .orderBy(F.col("trip_duration_hours").desc())

longest_df.show(5, truncate=False)

max_hours = longest_df.first()["trip_duration_hours"]
print(f">>> Longest trip on Oct 15 : {max_hours} hours")

# SQL approach — same result
spark.sql("""
    SELECT tpep_pickup_datetime,
           tpep_dropoff_datetime,
           trip_distance,
           ROUND(
               (UNIX_TIMESTAMP(tpep_dropoff_datetime) -
                UNIX_TIMESTAMP(tpep_pickup_datetime)) / 3600, 2
           ) AS trip_duration_hours
    FROM   taxi
    WHERE  DATE(tpep_pickup_datetime) = '2024-10-15'
    ORDER  BY trip_duration_hours DESC
    LIMIT  5
""").show(truncate=False)

# ── 5. Joins ──────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 5 — Joins")
print("="*60)

# Two join types:
# 1. Shuffle join (default) — both sides repartitioned by join key, expensive
# 2. Broadcast join — small table broadcast to all executors, no shuffle

# Broadcast join is appropriate here: zones is tiny (265 rows)
print(f"Zone table size: {df_zones.count()} rows — good broadcast candidate\n")

df_joined = df_taxi \
    .join(F.broadcast(df_zones),
          df_taxi["PULocationID"] == df_zones["LocationID"],
          how="left") \
    .withColumnRenamed("Zone", "pickup_zone") \
    .withColumnRenamed("Borough", "pickup_borough")

print("Joined schema (selected cols):")
df_joined.select(
    "tpep_pickup_datetime", "PULocationID",
    "pickup_zone", "pickup_borough", "fare_amount"
).show(5, truncate=False)

# ── 6. Homework Q4 — Least frequent pickup zone ───────────────────────────────
print("\n" + "="*60)
print("HOMEWORK Q4 — Least frequent pickup location zone")
print("="*60)

# DataFrame API
zone_counts = df_joined \
    .filter(F.col("pickup_zone").isNotNull()) \
    .groupBy("pickup_zone") \
    .count() \
    .orderBy(F.col("count").asc())

zone_counts.show(10)

least_frequent = zone_counts.first()
print(f">>> Least frequent zone : {least_frequent['pickup_zone']} "
      f"({least_frequent['count']:,} trips)")

# SQL approach — same result
spark.sql("""
    SELECT z.Zone         AS pickup_zone,
           COUNT(*)       AS trip_count
    FROM   taxi t
    LEFT   JOIN zones z ON t.PULocationID = z.LocationID
    WHERE  z.Zone IS NOT NULL
    GROUP  BY z.Zone
    ORDER  BY trip_count ASC
    LIMIT  10
""").show(truncate=False)

# ── 7. Bonus — Revenue by borough ─────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 7 — Revenue by pickup borough")
print("="*60)

spark.sql("""
    SELECT z.Borough                        AS borough,
           COUNT(*)                         AS trips,
           ROUND(SUM(t.total_amount), 2)    AS total_revenue,
           ROUND(AVG(t.fare_amount), 2)     AS avg_fare
    FROM   taxi t
    LEFT   JOIN zones z ON t.PULocationID = z.LocationID
    WHERE  z.Borough IS NOT NULL
    GROUP  BY z.Borough
    ORDER  BY total_revenue DESC
""").show()

# ── 8. Stop ───────────────────────────────────────────────────────────────────
spark.stop()
print("\nDone. SparkSession stopped.")
