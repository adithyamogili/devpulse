import json, time
import psycopg
from kafka import KafkaConsumer
from devpulse.config import settings

DDL = '''
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE TABLE IF NOT EXISTS bronze.github_api_records(
 repository_full_name TEXT NOT NULL, resource_type TEXT NOT NULL, record_id TEXT NOT NULL,
 payload JSONB NOT NULL, fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 PRIMARY KEY(repository_full_name, resource_type, record_id));
'''

def main():
    while True:
        try:
            consumer = KafkaConsumer(settings.kafka_topic,
                bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
                group_id="devpulse-bronze-writer", auto_offset_reset="earliest",
                enable_auto_commit=False, value_deserializer=lambda b: json.loads(b.decode()))
            with psycopg.connect(settings.database_url) as conn:
                conn.execute(DDL); conn.commit()
                print("Kafka consumer connected; waiting for GitHub records", flush=True)
                for message in consumer:
                    item = message.value
                    conn.execute('''INSERT INTO bronze.github_api_records
                    (repository_full_name,resource_type,record_id,payload,fetched_at)
                    VALUES (%s,%s,%s,%s::jsonb,NOW())
                    ON CONFLICT(repository_full_name,resource_type,record_id)
                    DO UPDATE SET payload=EXCLUDED.payload,fetched_at=NOW()''',
                    (item["repository_full_name"], item["resource_type"], item["record_id"], json.dumps(item["payload"])))
                    conn.commit()
                    consumer.commit()
        except Exception as exc:
            print(f"Consumer connection error: {exc}; retrying in 5 seconds", flush=True)
            time.sleep(5)

if __name__ == "__main__": main()
