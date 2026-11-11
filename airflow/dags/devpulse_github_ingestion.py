from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="devpulse_github_ingestion",
    description="Daily GitHub API extraction into MinIO and Kafka",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"owner":"devpulse", "retries":2, "retry_delay":timedelta(minutes=5)},
    tags=["devpulse","github","ingestion"],
) as dag:
    ingest_github = BashOperator(
        task_id="ingest_github_public_repositories",
        bash_command="PYTHONPATH=/opt/airflow python -m devpulse.cli ingest --max-pages 1",
    )
