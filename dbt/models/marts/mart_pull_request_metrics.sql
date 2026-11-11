
{{ config(materialized='table') }}

select
    repository_full_name,
    count(*) as pull_requests_seen,

    count(*) filter (
        where state = 'open'
    ) as open_pull_requests,

    count(*) filter (
        where state = 'closed'
    ) as closed_pull_requests,

    count(*) filter (
        where payload->>'merged_at' is not null
    ) as merged_pull_requests,

    count(distinct author_login) as distinct_pr_authors

from {{ ref('stg_github_records') }}

where resource_type = 'pull_requests'

group by repository_full_name
