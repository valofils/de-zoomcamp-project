# Module 6 — Stream Processing (PyFlink + Redpanda)

## Stack
| Service | Image | Port |
|---|---|---|
| Redpanda | redpandadata/redpanda:latest | 9092 (Kafka API), 8082 (REST) |
| Flink JobManager | flink:1.18-scala_2.12-java11 | 8083 (Web UI) |
| Flink TaskManager | flink:1.18-scala_2.12-java11 | — |
| PostgreSQL | postgres:15 | 5432 |

---

## Quickstart

### 1. Start services
```bash
cd 06-streaming/docker
docker-compose up -d
```

### 2. Verify Redpanda (Q1 — version)
```bash
docker exec -it redpanda-1 rpk version
```

### 3. Create the topic (Q2)
```bash
docker exec -it redpanda-1 rpk topic create green-trips
```

### 4. Create Postgres tables
```bash
psql -h localhost -p 5432 -U postgres -d postgres -f docker/init.sql
# password: postgres
```

### 5. Install Python deps
```bash
pip install kafka-python
```

### 6. Test connection (Q3)
```bash
python3 06-streaming/notebooks/verify_setup.py
```

### 7. Send taxi data (Q4)
```bash
python3 06-streaming/producers/producer.py
```

---

## Flink Web UI
http://localhost:8083

## Homework Questions
| Q | Topic |
|---|---|
| Q1 | Redpanda version (`rpk version`) |
| Q2 | Create `green-trips` topic |
| Q3 | `producer.bootstrap_connected()` output |
| Q4 | Time to send + flush entire dataset |
| Q5 | Session window — longest unbroken streak |
