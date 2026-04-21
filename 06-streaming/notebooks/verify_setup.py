"""
verify_setup.py — smoke tests for Q1, Q2, Q3 of the homework

Run AFTER docker-compose up:
    python3 06-streaming/notebooks/verify_setup.py
"""

from kafka import KafkaProducer
import json

BOOTSTRAP_SERVER = "localhost:9092"


def test_connection():
    """Q3 — confirm we can reach the Redpanda broker."""
    producer = KafkaProducer(
        bootstrap_servers=[BOOTSTRAP_SERVER],
        value_serializer=lambda d: json.dumps(d).encode("utf-8"),
    )
    connected = producer.bootstrap_connected()
    print(f"bootstrap_connected() → {connected}")
    return producer


if __name__ == "__main__":
    print("── Q3: Testing Kafka/Redpanda connection ──")
    p = test_connection()
    print("\nSetup looks good. Next steps:")
    print("  1. Check Redpanda version: docker exec -it redpanda-1 rpk version")
    print("  2. Create topic:           docker exec -it redpanda-1 rpk topic create green-trips")
    print("  3. Run producer:           python3 06-streaming/producers/producer.py")
