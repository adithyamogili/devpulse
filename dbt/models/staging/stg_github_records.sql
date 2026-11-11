{{ config(materialized='view') }}
select
  repository_full_name,
  resource_type,
  record_id,
  payload,
  fetched_at,
  coalesce(payload->>'created_at', payload#>>'{commit,author,date}') as created_at_text,
  payload->>'updated_at' as updated_at_text,
  coalesce(payload#>>'{user,login}', payload#>>'{author,login}') as author_login,
  payload->>'state' as state,
  payload->>'title' as title
from bronze.github_api_records
