"""Demo role-based access seam.

There is no real authentication in this portfolio app. The frontend's role
switcher sends the active role on every request via the `X-Demo-Role`
header; `require_role` is a FastAPI dependency that validates it against
a per-route allowlist.

This is intentionally the *only* place that knows about "auth" so that a
real scheme (JWT/OAuth) can later replace just this module without
touching routers or services.
"""
from enum import StrEnum

from fastapi import Header, HTTPException, status


class Role(StrEnum):
    OPERATIONS_MANAGER = "operations_manager"
    INTAKE_SPECIALIST = "intake_specialist"
    AUTHORIZATION_SPECIALIST = "authorization_specialist"


def require_role(*allowed: Role):
    """Build a FastAPI dependency that only allows the given roles."""

    async def _dependency(x_demo_role: str = Header(default=Role.OPERATIONS_MANAGER.value)) -> Role:
        try:
            role = Role(x_demo_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown role '{x_demo_role}'",
            )
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role.value}' is not permitted for this action",
            )
        return role

    return _dependency


# Any authenticated demo role — used on routes all three roles may access.
any_role = require_role(*Role)


async def get_current_user_name(
    x_demo_user: str = Header(default="Demo User"),
) -> str:
    """The demo 'signed in as' display name, used for audit-log attribution.

    Sent by the frontend's role switcher alongside X-Demo-Role. Defaults to
    a generic label so the API works fine even without it (e.g. via /docs).
    """
    return x_demo_user
