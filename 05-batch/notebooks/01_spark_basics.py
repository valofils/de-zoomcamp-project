"""
Module 5 — Batch Processing with Apache Spark
Script 01: Spark Basics

Topics:
- SparkSession setup
- Reading Parquet
- Schema inspection
- Transformations (select, withColumn, filter)
- Repartitioning
- Writing Parquet
- Homework Q1: average parquet file size after repartition(4)
- Homework Q2: trips starting on October 15
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# ── 0. Paths ──────────────────────────────────────────────────────────────────
BASE_DIR  = "/workspaces/de-zoomcamp-project/05-batch"
DATA_PATH = f"{BASE_DIR}/data/yellow_tripdata_2024-10.parquet"
OUT_PATH  = f"{BASE_DIR}/data/yellow_oct2024_4partitions"

# ── 1. SparkSession ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 1 — SparkSession")
print("="*60)

spark = SparkSession.builder \
    .master("local[*]") \
    .appName("dezoomcamp-module5-basics") \
    .config("spark.api.mode", "classic") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print(f"Spark version : {spark.version}")
print(f"Cores         : {spark.sparkContext.defaultParallelism}")

# ── 2. Read Parquet ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 2 — Read Parquet")
print("="*60)

df = spark.read.parquet(DATA_PATH)

print(f"Row count     : {df.count():,}")
print(f"Columns       : {len(df.columns)}")

# ── 3. Schema ─────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 3 — Schema")
print("="*60)

df.printSchema()
df.show(5, truncate=False)

# ── 4. Transformations ────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 4 — Transformations")
print("="*60)

df_enriched = df \
    .select(
        "VendorID",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "PULocationID",
        "DOLocationID",
        "fare_amount",
        "total_amount"
    ) \
    .withColumn("pickup_date", F.to_date("tpep_pickup_datetime")) \
    .withColumn("pickup_hour", F.hour("tpep_pickup_datetime")) \
    .withColumn("trip_duration_min",
        F.round(
            (F.unix_timestamp("tpep_dropoff_datetime") -
             F.unix_timestamp("tpep_pickup_datetime")) / 60, 2
        ))

df_valid = df_enriched.filter(
    (F.col("trip_distance")    > 0) &
    (F.col("fare_amount")      > 0) &
    (F.col("trip_duration_min") > 0) &
    (F.col("trip_duration_min") < 300)
)

total     = df.count()
valid     = df_valid.count()
print(f"Total rows    : {total:,}")
print(f"Valid rows    : {valid:,}")
print(f"Dropped       : {total - valid:,}")

# ── 5. Partitioning ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 5 — Partitioning")
print("="*60)

df_raw = spark.read.parquet(DATA_PATH)
print(f"Default partitions : {df_raw.rdd.getNumPartitions()}")

df_4 = df_raw.repartition(4)
print(f"After repartition  : {df_4.rdd.getNumPartitions()}")

# ── 6. Write Parquet ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 6 — Write Parquet")
print("="*60)

df_4.write.mode("overwrite").parquet(OUT_PATH)
print(f"Written to: {OUT_PATH}")

# ── 7. Homework Q1: average file size ────────────────────────────────────────
print("\n" + "="*60)
print("HOMEWORK Q1 — Average Parquet file size")
print("="*60)

parquet_files = [
    f for f in os.listdir(OUT_PATH)
    if f.endswith(".parquet")
]

sizes_mb = [
    os.path.getsize(os.path.join(OUT_PATH, f)) / (1024 ** 2)
    for f in parquet_files
]

print(f"Files created  : {len(parquet_files)}")
print(f"Sizes (MB)     : {[round(s, 2) for s in sizes_mb]}")
print(f">>> Average    : {sum(sizes_mb)/len(sizes_mb):.2f} MB")

# ── 8. Homework Q2: trips on October 15 ──────────────────────────────────────
print("\n" + "="*60)
print("HOMEWORK Q2 — Trips starting on October 15")
print("="*60)

oct15_count = df_raw.filter(
    F.to_date(F.col("tpep_pickup_datetime")) == F.lit("2024-10-15")
).count()

print(f">>> Trips on Oct 15 : {oct15_count:,}")

# ── 9. Quick EDA ──────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 9 — Trips per day (EDA)")
print("="*60)

df_raw \
    .withColumn("pickup_date", F.to_date("tpep_pickup_datetime")) \
    .groupBy("pickup_date") \
    .count() \
    .orderBy("pickup_date") \
    .show(35)

# ── 10. Stop ──────────────────────────────────────────────────────────────────
spark.stop()
print("\nDone. SparkSession stopped.")
