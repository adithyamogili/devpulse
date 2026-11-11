{{ config(materialized='table') }}
select
  repository_full_name,
  count(*) filter (where resource_type = 'commits') as commit_records,
  count(*) filter (where resource_type = 'issues') as issue_records,
  count(*) filter (where resource_type = 'pull_requests') as pull_request_records,
  count(*) filter (where resource_type = 'contributors') as contributor_records,
  count(*) as total_records,
  max(fetched_at) as last_fetched_at
from {{ ref('stg_github_records') }}
group by repository_full_name
