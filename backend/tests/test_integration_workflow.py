from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import get_settings
from app.main import app


def _token() -> str:
    s = get_settings()
    return jwt.encode({"sub": "op", "roles": ["operator", "risk_officer"], "attributes": {"lob": "trade"}, "iss": s.jwt_issuer, "aud": s.jwt_audience}, s.jwt_secret, algorithm="HS256")


def test_workflow_policy_block() -> None:
    client = TestClient(app)
    t = _token()
    payload = {"workflow_id": "wf1", "input_payload": {"contains_pii": True, "pii_redacted": False}, "provider": "llama_vision"}
    r = client.post("/api/v1/workflow-runs", headers={"Authorization": f"Bearer {t}"}, json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "blocked_by_policy"
