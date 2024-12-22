import pytest
import requests
from config.config import TestConfig

@pytest.fixture(scope="session")
def api_client():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0",
        "Accept": "application/json"
    })
    return session

@pytest.fixture(scope="session")
def base_url():
    return TestConfig.BASE_URL