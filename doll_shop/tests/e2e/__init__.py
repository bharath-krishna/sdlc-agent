from fastapi.testclient import TestClient


class MockUser:
    def __init__(self, access_token):
        self.access_token = access_token


class CustomClient(TestClient):
    def __init__(self, app, user=None, **kwargs):
        super().__init__(app, **kwargs)
        self.user = user

    def request(self, method, url, **kwargs):
        if self.user:
            headers = kwargs.get("headers") or {}
            headers["Authorization"] = f"Bearer {self.user.access_token}"
            kwargs["headers"] = headers
        return super().request(method, url, **kwargs)
