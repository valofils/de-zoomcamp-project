#!/usr/bin/env bash
# run_session_job.sh
# Copies session_job.py into jobmanager, installs Kafka connector JAR, runs it.
# Run from repo root: bash 06-streaming/notebooks/run_session_job.sh

set -e

JOB_FILE="06-streaming/notebooks/session_job.py"
CONTAINER="jobmanager"
FLINK_LIB="/opt/flink/lib"
KAFKA_JAR="flink-sql-connector-kafka-3.1.0-1.18.jar"
KAFKA_JAR_URL="https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.1.0-1.18/${KAFKA_JAR}"

echo "── Copying session_job.py into $CONTAINER ──"
docker cp "$JOB_FILE" "$CONTAINER:/opt/session_job.py"

echo "── Downloading Kafka SQL connector JAR (if not present) ──"
docker exec "$CONTAINER" bash -c "
    if [ ! -f ${FLINK_LIB}/${KAFKA_JAR} ]; then
        wget -q -P ${FLINK_LIB} ${KAFKA_JAR_URL}
        echo 'JAR downloaded.'
    else
        echo 'JAR already present.'
    fi
"

echo "── Running session_job.py ──"
docker exec -it "$CONTAINER" python3 /opt/session_job.py
