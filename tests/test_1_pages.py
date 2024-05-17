import os
import sys

from fastapi.testclient import TestClient
import pytest
import requests


@pytest.fixture
def get_client():
    sys.path.append(os.getcwd())
    from main import app
    client = TestClient(app)
    yield client


@pytest.mark.run_server
@pytest.mark.parametrize("page", ['/', '/generate', '/generate/algorithmic', '/generate/neural', '/about_us', '/help/generators_type'])
def test_pages_1(page, get_client):
    client = get_client
    response = client.get(page)
    assert response.status_code == 200


@pytest.mark.parametrize("page", ['/', '/generate', '/generate/algorithmic', '/generate/neural', '/about_us', '/help/generators_type'])
def test_pages_2(page, get_ip, get_port, get_max_timeout):
    ip, port, max_timeout = get_ip, get_port, get_max_timeout
    response = requests.get(f'http://{ip}:{port}{page}', timeout=max_timeout)
    assert response.status_code == 200
