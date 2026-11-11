from devpulse.config import settings
from devpulse.github_client import GitHubClient, split_repo
from devpulse.storage import ensure_bucket, make_producer, publish_record

def ingest(repositories=None, max_pages=1):
    targets = repositories or settings.repository_list
    s3 = ensure_bucket()
    producer = make_producer()
    totals = {}
    try:
        with GitHubClient(settings.github_api_base_url, settings.github_token,
                          settings.github_timeout_seconds, settings.github_max_retries) as gh:
            for full_name in targets:
                owner, repo = split_repo(full_name)
                prefix = f"repos/{owner}/{repo}"
                print(f"Fetching {full_name}")
                collections = {
                    "repository": [gh.get_json(prefix)],
                    "issues": gh.paginate(prefix + "/issues", {"state":"all","sort":"updated","direction":"desc"}, max_pages),
                    "pull_requests": gh.paginate(prefix + "/pulls", {"state":"all","sort":"updated","direction":"desc"}, max_pages),
                    "commits": gh.paginate(prefix + "/commits", {}, max_pages),
                    "contributors": gh.paginate(prefix + "/contributors", {}, max_pages),
                }
                counts = {}
                for kind, records in collections.items():
                    for record in records:
                        publish_record(producer, s3, full_name, kind, record)
                    counts[kind] = len(records)
                totals[full_name] = counts
                print(f"  published {sum(counts.values())} records: {counts}")
        producer.flush(timeout=30)
    finally:
        producer.close()
    return totals
