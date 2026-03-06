from app.core.security import UserContext


class PolicyEngine:
    def evaluate(self, payload: dict, user: UserContext) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        if not payload.get("trade_documents"):
            reasons.append("trade_documents are mandatory for LC scrutiny workflows")
        if payload.get("contains_pii") is True and not payload.get("pii_redacted"):
            reasons.append("PII must be redacted before model execution")
        if payload.get("risk_tier") == "high" and "risk_officer" not in user.roles:
            reasons.append("risk_officer role required for high risk_tier requests")
        return (len(reasons) == 0), reasons
