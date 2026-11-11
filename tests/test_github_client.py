import httpx
import pytest
from devpulse.github_client import GitHubClient, GitHubAPIError, split_repo

def test_split_repo():
    assert split_repo("owner/repo") == ["owner","repo"]

@pytest.mark.parametrize("value", ["", "owner", "a/b/c", "/repo", "owner/"])
def test_invalid_repo(value):
    with pytest.raises(ValueError): split_repo(value)

def test_get_json_mocked():
    mock = httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, json={"ok": True})))
    client = GitHubClient("https://api.github.com", max_retries=0)
    client.http.close()
    client.http = mock
    assert client.get_json("repos/a/b") == {"ok": True}
    client.close()

def test_http_error():
    mock = httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(404, text="missing")))
    client = GitHubClient("https://api.github.com", max_retries=0)
    client.http.close()
    client.http = mock
    with pytest.raises(GitHubAPIError): client.get_json("repos/no/no")
    client.close()
