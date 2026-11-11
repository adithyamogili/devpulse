import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://devpulse:devpulse@localhost:5432/devpulse"
    github_token: str | None = None
    github_api_base_url: str = "https://api.github.com"
    github_timeout_seconds: float = 30.0
    github_max_retries: int = 3
    github_repositories: str = "adithyamogili/mailmon-backend,adithyamogili/mailmon-frontend,adithyamogili/Metatconvo,adithyamogili/olist-data-engineering,fastapi/fastapi,django/django,apache/airflow"
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "github-raw"
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic: str = "github.raw.records"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def repository_list(self):
        return [x.strip() for x in self.github_repositories.split(",") if x.strip()]

settings = Settings()
