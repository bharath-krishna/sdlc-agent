import pytest
import jwt
from datetime import datetime, timedelta, timezone
from api.configurations.base import config
from tests.e2e import MockUser, CustomClient
from api.main import app


@pytest.fixture
def mock_user_token():
    payload = {
        "sub": "1234567890",
        "name": "Test User",
        "id": "test-user-id",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    }
    return jwt.encode(payload, config.signature_text, algorithm="HS256")


@pytest.fixture
def mock_user(mock_user_token):
    return MockUser(access_token=mock_user_token)


@pytest.fixture
def user_client(mock_user):
    return CustomClient(app, user=mock_user)
