import time
import httpx

class GitHubAPIError(RuntimeError): pass
class GitHubRateLimitError(GitHubAPIError): pass

class GitHubClient:
    def __init__(self, base_url, token=None, timeout=30, max_retries=3):
        headers = {"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"DevPulse"}
        if token: headers["Authorization"] = f"Bearer {token}"
        self.base_url = base_url.rstrip("/")
        self.http = httpx.Client(headers=headers, timeout=timeout, follow_redirects=True)
        self.max_retries = max_retries

    def close(self): self.http.close()
    def __enter__(self): return self
    def __exit__(self, *args): self.close()

    def get_json(self, path, params=None):
        for attempt in range(self.max_retries + 1):
            try:
                response = self.http.get(f"{self.base_url}/{path.lstrip('/')}", params=params)
            except httpx.RequestError as exc:
                if attempt >= self.max_retries: raise GitHubAPIError(str(exc)) from exc
                time.sleep(min(2 ** attempt, 8)); continue
            if response.status_code in (403,429):
                retry_after = response.headers.get("Retry-After")
                if retry_after and attempt < self.max_retries:
                    time.sleep(min(float(retry_after), 30)); continue
                if response.headers.get("X-RateLimit-Remaining") == "0":
                    raise GitHubRateLimitError("GitHub API rate limit exhausted; wait for reset or add GITHUB_TOKEN.")
            if response.status_code >= 500 and attempt < self.max_retries:
                time.sleep(min(2 ** attempt, 8)); continue
            if response.is_error:
                raise GitHubAPIError(f"GitHub HTTP {response.status_code}: {response.text[:300]}")
            return response.json()
        raise GitHubAPIError("GitHub request retries exhausted")

    def paginate(self, path, params=None, max_pages=1):
        if max_pages < 1: raise ValueError("max_pages must be >= 1")
        query = dict(params or {})
        query["per_page"] = 100
        records = []
        for page in range(1, max_pages + 1):
            query["page"] = page
            batch = self.get_json(path, query)
            if not isinstance(batch, list): raise GitHubAPIError(f"Expected list from {path}")
            records.extend(batch)
            if len(batch) < 100: break
        return records

def split_repo(full_name):
    parts = full_name.strip().split("/")
    if len(parts) != 2 or not all(parts): raise ValueError(f"Expected owner/repo, got {full_name!r}")
    return parts
