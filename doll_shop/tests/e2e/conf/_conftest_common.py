import pytest
from tests.e2e import CustomClient
from api.main import app


@pytest.fixture
def function_client():
    return CustomClient(app)
