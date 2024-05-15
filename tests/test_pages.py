import os
import sys

from fastapi.testclient import TestClient
import pytest
import requests


IP = '127.0.0.1'


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
def test_pages_2(page, get_port):
    port = get_port
    response = requests.get(f'http://{IP}:{port}{page}')
    assert response.status_code == 200
