import hashlib
import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import AuditLog


def append_audit_log(db: Session, actor_id: str, action: str, resource: str, details: dict) -> AuditLog:
    payload = json.dumps(details, sort_keys=True)
    digest = hashlib.sha256(f"{actor_id}:{action}:{resource}:{payload}".encode()).hexdigest()
    row = AuditLog(
        id=str(uuid4()),
        actor_id=actor_id,
        action=action,
        resource=resource,
        details=details,
        immutable_hash=digest,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
