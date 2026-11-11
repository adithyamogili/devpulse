import json
from datetime import datetime, timezone
import boto3
from botocore.client import Config
from kafka import KafkaProducer
from devpulse.config import settings

def minio_client():
    return boto3.client("s3", endpoint_url=f"http://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key, aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"), region_name="us-east-1")

def ensure_bucket():
    client = minio_client()
    try: client.head_bucket(Bucket=settings.minio_bucket)
    except Exception: client.create_bucket(Bucket=settings.minio_bucket)
    return client

def make_producer():
    return KafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
        value_serializer=lambda value: json.dumps(value, default=str).encode("utf-8"),
        retries=5, acks="all", linger_ms=20)

def publish_record(producer, s3, repository, resource_type, record):
    rid = record.get("sha") if resource_type == "commits" else record.get("id")
    if resource_type == "repository": rid = record.get("id") or record.get("full_name")
    if resource_type == "contributors": rid = record.get("id") or record.get("login")
    if rid is None: raise ValueError(f"Missing ID for {resource_type}")
    fetched = datetime.now(timezone.utc)
    envelope = {"repository_full_name": repository, "resource_type": resource_type,
        "record_id": str(rid), "fetched_at": fetched.isoformat(), "payload": record}
    key = f"{repository}/{resource_type}/{rid}.json"
    s3.put_object(Bucket=settings.minio_bucket, Key=key,
        Body=json.dumps(envelope, default=str).encode(), ContentType="application/json")
    producer.send(settings.kafka_topic, key=f"{repository}:{resource_type}:{rid}".encode(), value=envelope)
    return envelope
