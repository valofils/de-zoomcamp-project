#!/usr/bin/env python3
import os
import argparse
import requests
from pathlib import Path
from io import BytesIO

import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
DATA_DIR = Path("data/raw")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",     default=os.getenv("POSTGRES_HOST", "localhost"))
    parser.add_argument("--port",     default=os.getenv("POSTGRES_PORT", "5432"))
    parser.add_argument("--db",       default=os.getenv("POSTGRES_DB", "ny_taxi"))
    parser.add_argument("--user",     default=os.getenv("POSTGRES_USER", "root"))
    parser.add_argument("--password", default=os.getenv("POSTGRES_PASSWORD", "root"))
    parser.add_argument("--year",     type=int, default=2023)
    parser.add_argument("--months",   type=int, nargs="+", default=[1])
    parser.add_argument("--table",    default="yellow_taxi_trips")
    parser.add_argument("--chunk-size", type=int, default=100_000)
    return parser.parse_args()


def download_parquet(year, month):
    filename = f"yellow_tripdata_{year}-{month:02d}.parquet"
    url = f"{BASE_URL}/{filename}"
    local_path = DATA_DIR / filename

    if local_path.exists():
        print(f"  Using cached: {local_path}")
        return pd.read_parquet(local_path)

    print(f"  Downloading: {url}")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    buf = BytesIO()
    with tqdm(total=total, unit="iB", unit_scale=True, desc=filename) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            buf.write(chunk)
            bar.update(len(chunk))

    buf.seek(0)
    df = pd.read_parquet(buf)
    df.to_parquet(local_path, index=False)
    print(f"  Saved {len(df):,} rows to {local_path}")
    return df


def clean_dataframe(df):
    df.columns = [c.lower() for c in df.columns]
    for col in [c for c in df.columns if "datetime" in c]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    if "tpep_pickup_datetime" in df.columns:
        df = df.dropna(subset=["tpep_pickup_datetime"])
    if "fare_amount" in df.columns:
        df = df[df["fare_amount"] >= 0]
    return df


def load_to_postgres(df, engine, table, chunk_size, first_batch):
    for i, start in enumerate(tqdm(range(0, len(df), chunk_size), desc="  Loading")):
        chunk = df.iloc[start:start + chunk_size]
        chunk.to_sql(
            table, con=engine,
            if_exists="replace" if (i == 0 and first_batch) else "append",
            index=False, method="multi"
        )
    print(f"  Loaded {len(df):,} rows into '{table}'")


def main():
    args = get_args()
    engine = create_engine(
        f"postgresql://{args.user}:{args.password}@{args.host}:{args.port}/{args.db}"
    )

    print(f"\nNYC Taxi Ingestion → {args.host}:{args.port}/{args.db}")
    print(f"Year: {args.year}  Months: {args.months}\n")

    for i, month in enumerate(args.months):
        print(f"\n[Month {month:02d}]")
        df = download_parquet(args.year, month)
        df = clean_dataframe(df)
        load_to_postgres(df, engine, args.table, args.chunk_size, first_batch=(i == 0))

    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {args.table}")).scalar()
    print(f"\nDone! Total rows: {count:,}")


if __name__ == "__main__":
    main()