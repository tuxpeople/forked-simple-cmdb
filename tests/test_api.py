def test_api_no_token_required_when_unset(client):
    response = client.get('/api/stats')
    assert response.status_code == 200


def test_api_requires_token_when_configured(client, tmp_path, monkeypatch):
    import conftest

    app = conftest._load_app(tmp_path, monkeypatch, api_tokens='token-1')
    tokenless_client = app.test_client()
    response = tokenless_client.get('/api/stats')
    assert response.status_code == 401


def test_api_accepts_valid_token(authed_client):
    response = authed_client.get('/api/stats')
    assert response.status_code == 200


def test_add_server_requires_hostname(authed_client):
    response = authed_client.post('/api/server/add', json={})
    assert response.status_code == 400
    assert response.get_json()['success'] is False


def test_add_server_succeeds(authed_client):
    response = authed_client.post(
        '/api/server/add',
        json={'hostname': 'web01', 'ip_address': '192.168.1.10'}
    )
    assert response.status_code == 200
    assert response.get_json()['success'] is True
