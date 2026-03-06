from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt

from app.core.config import Settings, get_settings


@dataclass
class UserContext:
    sub: str
    roles: list[str]
    attributes: dict[str, Any]


def _decode_token(token: str, settings: Settings) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], audience=settings.jwt_audience, issuer=settings.jwt_issuer)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return payload


def get_current_user(request: Request, settings: Settings = Depends(get_settings)) -> UserContext:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = auth_header.replace("Bearer ", "", 1)
    payload = _decode_token(token, settings)
    return UserContext(
        sub=payload.get("sub", "unknown"),
        roles=payload.get("roles", []),
        attributes=payload.get("attributes", {}),
    )


def require_permission(action: str):
    def checker(user: UserContext = Depends(get_current_user)) -> UserContext:
        role_map = {
            "agents:create": {"admin", "agent_admin"},
            "workflow:run": {"admin", "operator"},
            "maker_checker:resolve": {"admin", "checker"},
        }
        if not set(user.roles).intersection(role_map.get(action, set())):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RBAC denied")
        return user

    return checker


def evaluate_abac(user: UserContext, resource_attrs: dict[str, Any]) -> None:
    user_lob = user.attributes.get("lob")
    resource_lob = resource_attrs.get("lob")
    if resource_lob and user_lob and user_lob != resource_lob:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ABAC denied")
