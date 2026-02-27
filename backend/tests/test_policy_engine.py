from app.services.policy_engine import PolicyEngine


def test_policy_rejects_missing_docs() -> None:
    allowed, reasons = PolicyEngine().evaluate({"contains_pii": False})
    assert not allowed
    assert reasons


def test_policy_accepts_valid_payload() -> None:
    allowed, reasons = PolicyEngine().evaluate(
        {
            "trade_documents": ["invoice"],
            "contains_pii": True,
            "pii_redacted": True,
        }
    )
    assert allowed
    assert reasons == []
