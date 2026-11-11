from devpulse.config import settings

def test_repository_config_has_seven_repositories():
    assert len(settings.repository_list) == 7
    assert "apache/airflow" in settings.repository_list
