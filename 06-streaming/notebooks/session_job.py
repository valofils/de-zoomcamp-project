"""
session_job.py — Q5: PyFlink session window on green-trips topic

Uses Flink SQL with the classic GROUP BY SESSION(...) syntax (works in 1.18).
Finds the (PULocationID, DOLocationID) pair with the longest unbroken
streak of taxi trips using a SESSION window with a 5-minute gap.

Run from repo root:
    bash 06-streaming/notebooks/run_session_job.sh
"""

import logging
from pyflink.table import EnvironmentSettings, TableEnvironment

logging.basicConfig(level=logging.INFO)


def main():
    env_settings = EnvironmentSettings.in_streaming_mode()
    t_env = TableEnvironment.create(env_settings)
    t_env.get_config().set("parallelism.default", "1")

    # ── Source table ──────────────────────────────────────────────────────────
    t_env.execute_sql("""
        CREATE TABLE green_trips (
            lpep_pickup_datetime  STRING,
            lpep_dropoff_datetime STRING,
            PULocationID          STRING,
            DOLocationID          STRING,
            passenger_count       STRING,
            trip_distance         STRING,
            tip_amount            STRING,
            dropoff_ts AS TO_TIMESTAMP(lpep_dropoff_datetime, 'yyyy-MM-dd HH:mm:ss'),
            WATERMARK FOR dropoff_ts AS dropoff_ts - INTERVAL '5' SECOND
        ) WITH (
            'connector'                    = 'kafka',
            'topic'                        = 'green-trips',
            'properties.bootstrap.servers' = 'redpanda-1:29092',
            'properties.group.id'          = 'flink-session-job',
            'scan.startup.mode'            = 'earliest-offset',
            'format'                       = 'json',
            'json.ignore-parse-errors'     = 'true'
        )
    """)

    # ── Sink: print to stdout ─────────────────────────────────────────────────
    t_env.execute_sql("""
        CREATE TABLE session_results (
            PULocationID STRING,
            DOLocationID STRING,
            trip_count   BIGINT,
            window_start TIMESTAMP(3),
            window_end   TIMESTAMP(3)
        ) WITH (
            'connector' = 'print'
        )
    """)

    # ── Classic GROUP BY SESSION window syntax (Flink 1.13–1.18 compatible) ──
    result = t_env.execute_sql("""
        INSERT INTO session_results
        SELECT
            PULocationID,
            DOLocationID,
            COUNT(*)                                        AS trip_count,
            SESSION_START(dropoff_ts, INTERVAL '5' MINUTE) AS window_start,
            SESSION_END(dropoff_ts, INTERVAL '5' MINUTE)   AS window_end
        FROM green_trips
        GROUP BY
            PULocationID,
            DOLocationID,
            SESSION(dropoff_ts, INTERVAL '5' MINUTE)
    """)

    result.wait()


if __name__ == "__main__":
    main()
