{{ config(materialized='table') }}
select
  repository_full_name,
  count(*) as issues_seen,
  count(*) filter (where state = 'open') as open_issues,
  count(*) filter (where state = 'closed') as closed_issues,
  count(distinct author_login) as distinct_issue_authors
from {{ ref('stg_github_records') }}
where resource_type = 'issues'
group by repository_full_name
