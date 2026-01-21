import importlib
import sys
from pathlib import Path

import pytest


def _load_app(tmp_path, monkeypatch, api_tokens=None):
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / 'test.db'))
    monkeypatch.setenv('SECRET_KEY', 'test-secret')
    if api_tokens is None:
        monkeypatch.delenv('API_TOKENS', raising=False)
    else:
        monkeypatch.setenv('API_TOKENS', api_tokens)

    module = sys.modules.get('app')
    if module is None:
        module = importlib.import_module('app')
    module = importlib.reload(module)
    module.init_db()
    return module.app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    app = _load_app(tmp_path, monkeypatch)
    return app.test_client()


@pytest.fixture()
def authed_client(tmp_path, monkeypatch):
    app = _load_app(tmp_path, monkeypatch, api_tokens='token-1')
    client = app.test_client()
    client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer token-1'
    return client
