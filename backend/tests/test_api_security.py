from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import get_settings
from app.main import app


def _token(roles: list[str]) -> str:
    s = get_settings()
    return jwt.encode({"sub": "tester", "roles": roles, "attributes": {"lob": "trade"}, "iss": s.jwt_issuer, "aud": s.jwt_audience}, s.jwt_secret, algorithm="HS256")


def test_health_open() -> None:
    client = TestClient(app)
    assert client.get("/api/v1/health").status_code == 200


def test_agents_requires_auth() -> None:
    client = TestClient(app)
    r = client.post("/api/v1/agents", json={"name": "xxy", "description": "d", "owner_team": "trade", "guardrail_bundle": "default"})
    assert r.status_code == 401


def test_agents_rbac_forbidden() -> None:
    client = TestClient(app)
    token = _token(["operator"])
    r = client.post("/api/v1/agents", headers={"Authorization": f"Bearer {token}"}, json={"name": "agent-1", "description": "d", "owner_team": "trade", "guardrail_bundle": "default"})
    assert r.status_code == 403
