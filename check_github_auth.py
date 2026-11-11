
import os
import httpx

token = os.getenv("GITHUB_TOKEN")

if not token:
    print("GITHUB_TOKEN is missing")
    raise SystemExit(1)

response = httpx.get(
    "https://api.github.com/rate_limit",
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    },
    timeout=15,
)

print("HTTP Status:", response.status_code)

if response.status_code == 200:
    print("Remaining requests:", response.json()["rate"]["remaining"])
    print("GitHub authentication successful!")
else:
    print("Authentication check failed:", response.text[:300])
