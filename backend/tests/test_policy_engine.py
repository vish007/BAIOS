from app.core.security import UserContext
from app.services.policy_engine import PolicyEngine


def test_policy_rejects_missing_docs() -> None:
    user = UserContext(sub="u1", roles=["operator"], attributes={"lob": "trade"})
    allowed, reasons = PolicyEngine().evaluate({"contains_pii": False}, user=user)
    assert not allowed
    assert reasons


def test_policy_accepts_valid_payload() -> None:
    user = UserContext(sub="u1", roles=["operator", "risk_officer"], attributes={"lob": "trade"})
    allowed, reasons = PolicyEngine().evaluate(
        {
            "trade_documents": ["invoice"],
            "contains_pii": True,
            "pii_redacted": True,
            "risk_tier": "high",
        },
        user=user,
    )
    assert allowed
    assert reasons == []
