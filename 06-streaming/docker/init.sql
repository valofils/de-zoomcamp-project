-- Run these after docker-compose is up:
--   pgcli -h localhost -p 5432 -u postgres -d postgres
--   then paste this file, or:
--   psql -h localhost -p 5432 -U postgres -d postgres -f init.sql

CREATE TABLE IF NOT EXISTS processed_events (
    test_data INTEGER,
    event_timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processed_events_aggregated (
    event_hour TIMESTAMP,
    test_data INTEGER,
    num_hits INTEGER
);
