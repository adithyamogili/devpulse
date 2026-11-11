# Operations and troubleshooting

## Startup order
Docker Compose starts PostgreSQL, MinIO, Kafka, the consumer, Airflow and dashboard.
Airflow initialization runs database migrations and creates the local admin user.

## GitHub rate limits
Unauthenticated public REST requests have a lower per-IP limit. If a run reports rate limit
exhaustion, wait for reset or add a read-only token to `.env` as `GITHUB_TOKEN`. Never paste
the token into source code or commit `.env`.

## No rows in dashboard
1. Check `docker compose logs kafka-consumer`.
2. Run a small ingestion command.
3. Allow the consumer to persist messages.
4. Run Spark enrichment and dbt.
5. Refresh the Streamlit page.

## Reset warning
`docker compose down -v` deletes the PostgreSQL, MinIO and Kafka volumes. Use only when you
intend to erase all locally collected data.
