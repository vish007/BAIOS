"""Policy and guardrail evaluator.

This module demonstrates where ABAC/RBAC, prompt safety, and business-policy
checks are applied prior to model invocation.
"""


class PolicyEngine:
    def evaluate(self, payload: dict) -> tuple[bool, list[str]]:
        reasons: list[str] = []

        # Simple developer-friendly checks; replace with OPA/Rego in production.
        if not payload.get("trade_documents"):
            reasons.append("trade_documents are mandatory for LC scrutiny workflows")

        if payload.get("contains_pii") is True and not payload.get("pii_redacted"):
            reasons.append("PII must be redacted before model execution")

        return (len(reasons) == 0), reasons
