"""
producer.py — send green taxi data to Redpanda topic 'green-trips'

Usage:
    pip install kafka-python
    python3 06-streaming/producers/producer.py

Data:
    https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz
"""

import json
import gzip
import urllib.request
import csv
import io
from time import time
from kafka import KafkaProducer

# ── Config ──────────────────────────────────────────────────────────────────
BOOTSTRAP_SERVER = "localhost:9092"
TOPIC_NAME = "green-trips"
DATA_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz"

KEEP_COLS = [
    "lpep_pickup_datetime",
    "lpep_dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "passenger_count",
    "trip_distance",
    "tip_amount",
]

# ── Serialiser ───────────────────────────────────────────────────────────────
def json_serializer(data):
    return json.dumps(data).encode("utf-8")


# ── Producer ─────────────────────────────────────────────────────────────────
def main():
    producer = KafkaProducer(
        bootstrap_servers=[BOOTSTRAP_SERVER],
        value_serializer=json_serializer,
    )

    print(f"Connected: {producer.bootstrap_connected()}")

    # Download and stream the gzipped CSV
    print(f"Downloading data from {DATA_URL} ...")
    with urllib.request.urlopen(DATA_URL) as response:
        with gzip.open(response, "rt", encoding="utf-8") as gz:
            reader = csv.DictReader(gz)

            t0 = time()
            count = 0

            for row in reader:
                message = {col: row[col] for col in KEEP_COLS if col in row}
                producer.send(TOPIC_NAME, value=message)
                count += 1
                if count % 10_000 == 0:
                    print(f"  Sent {count:,} messages...")

            producer.flush()
            t1 = time()

    print(f"\nDone. Sent {count:,} messages in {t1 - t0:.2f}s")


if __name__ == "__main__":
    main()
