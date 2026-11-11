CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;
CREATE SCHEMA IF NOT EXISTS ops;

CREATE TABLE IF NOT EXISTS bronze.github_api_records (
  repository_full_name TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  record_id TEXT NOT NULL,
  payload JSONB NOT NULL,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (repository_full_name, resource_type, record_id)
);
CREATE INDEX IF NOT EXISTS idx_bronze_resource ON bronze.github_api_records(resource_type);
CREATE INDEX IF NOT EXISTS idx_bronze_repository ON bronze.github_api_records(repository_full_name);
CREATE TABLE IF NOT EXISTS ops.ingestion_runs (
  run_id BIGSERIAL PRIMARY KEY,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMPTZ,
  repository_full_name TEXT,
  status TEXT NOT NULL,
  records_published INTEGER NOT NULL DEFAULT 0,
  error_message TEXT
);
CREATE TABLE IF NOT EXISTS silver.github_activity_enriched (
  repository_full_name TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  record_id TEXT NOT NULL,
  author_login TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  state TEXT,
  title TEXT,
  event_date DATE,
  payload JSONB NOT NULL,
  processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY(repository_full_name, resource_type, record_id)
);
