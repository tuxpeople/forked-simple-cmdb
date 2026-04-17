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


def test_upsert_server_creates_and_updates_by_hostname(authed_client):
    create_response = authed_client.post(
        '/api/server/upsert',
        json={
            'hostname': 'web01',
            'ip_address': '192.168.1.10',
            'environment': 'production',
            'cpu_cores': 4
        }
    )
    assert create_response.status_code == 200
    create_data = create_response.get_json()
    assert create_data['success'] is True
    assert create_data['action'] == 'created'

    update_response = authed_client.post(
        '/api/server/upsert',
        json={
            'hostname': 'web01',
            'ip_address': '192.168.1.11',
            'memory_gb': 16
        }
    )
    assert update_response.status_code == 200
    update_data = update_response.get_json()
    assert update_data['success'] is True
    assert update_data['action'] == 'updated'
    assert update_data['server_id'] == create_data['server_id']

    servers_response = authed_client.get('/api/servers')
    servers = servers_response.get_json()['servers']
    assert len(servers) == 1
    assert servers[0]['ip_address'] == '192.168.1.11'
    assert servers[0]['environment'] == 'production'
    assert servers[0]['cpu_cores'] == 4
    assert servers[0]['memory_gb'] == 16


def test_upsert_server_allows_explicit_null_to_clear_field(authed_client):
    authed_client.post(
        '/api/server/upsert',
        json={'hostname': 'web01', 'owner': 'platform'}
    )

    response = authed_client.post(
        '/api/server/upsert',
        json={'hostname': 'web01', 'owner': None}
    )

    assert response.status_code == 200
    server = authed_client.get('/api/servers').get_json()['servers'][0]
    assert server['owner'] is None


def test_upsert_server_requires_hostname(authed_client):
    response = authed_client.post('/api/server/upsert', json={})
    assert response.status_code == 400
    assert response.get_json()['success'] is False


def test_api_accepts_x_api_key(client, tmp_path, monkeypatch):
    import conftest

    app = conftest._load_app(tmp_path, monkeypatch, api_tokens='token-1')
    x_api_key_client = app.test_client()
    response = x_api_key_client.post(
        '/api/server/upsert',
        headers={'X-API-Key': 'token-1'},
        json={'hostname': 'web01'}
    )

    assert response.status_code == 200
    assert response.get_json()['success'] is True
