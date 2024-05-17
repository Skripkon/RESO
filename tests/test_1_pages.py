import pytest
import requests


@pytest.mark.parametrize("page", ['/', '/generate', '/generate/algorithmic', '/generate/neural', '/about_us', '/help/generators_type'])
def test_pages_2(page, get_ip, get_port, get_max_timeout):
    ip, port, max_timeout = get_ip, get_port, get_max_timeout
    response = requests.get(f'http://{ip}:{port}{page}', timeout=max_timeout)
    assert response.status_code == 200
