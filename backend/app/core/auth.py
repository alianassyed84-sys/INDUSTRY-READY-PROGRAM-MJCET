"""Authentication and authorization dependencies for FastAPI.

Standards-compliant JWT Bearer verification compatible with Clerk-issued tokens.
Verifies token signatures, issuer, expiry, and audience claims cryptographically.
Never trusts unverified claims.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

# Reusable HTTP Bearer extractor that does not raise automatically,
# allowing us to return custom, standards-compliant 401 error headers.
http_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedUser:
    """Verified identity extracted from a cryptographically validated JWT."""

    user_id: str
    email: str | None = None
    org_id: str | None = None
    roles: frozenset[str] = field(default_factory=frozenset)
    is_admin: bool = False
    claims: dict[str, Any] = field(default_factory=dict)


def _format_pem_key(key: str) -> str:
    """Normalize a PEM-encoded public key string."""
    clean = key.strip()
    if clean.startswith("-----BEGIN"):
        return clean
    # Wrap raw base64 key in standard PEM headers if omitted
    return f"-----BEGIN PUBLIC KEY-----\n{clean}\n-----END PUBLIC KEY-----"


class TokenVerifier:
    """Cryptographic token verification using Clerk public keys or JWKS."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._jwk_client: jwt.PyJWKClient | None = None
        if self.settings.clerk_jwks_url:
            self._jwk_client = jwt.PyJWKClient(self.settings.clerk_jwks_url)

    def verify_token(self, token: str) -> dict[str, Any]:
        """Verify token signature and return validated payload claims."""
        if not self.settings.auth_enabled or (
            self.settings.app_env == "development"
            and not (
                self.settings.clerk_pem_public_key
                or self.settings.clerk_jwks_url
                or self.settings.clerk_secret_key
            )
            and token in ("dev-bypass-token", "dev-token")
        ):
            # When explicitly disabled or running local dev without Clerk keys
            return {
                "sub": "test_user_anonymous",
                "role": "admin",
            }

        try:
            unverified_headers = jwt.get_unverified_header(token)
            algorithm = unverified_headers.get("alg", "RS256")
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format.",
                headers={
                    "WWW-Authenticate": (
                        'Bearer error="invalid_token", '
                        'error_description="Malformed token"'
                    )
                },
            ) from exc

        signing_key: Any = None
        algorithms: list[str] = []

        if self.settings.clerk_pem_public_key:
            signing_key = _format_pem_key(self.settings.clerk_pem_public_key)
            algorithms.append("RS256")
        elif self._jwk_client is not None:
            signing_key = self._jwk_client.get_signing_key_from_jwt(token).key
            algorithms.append("RS256")
        elif self.settings.clerk_secret_key:
            # Fallback for development/testing symmetric verification
            signing_key = self.settings.clerk_secret_key
            algorithms.append("HS256")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Authentication provider is enabled but no "
                    "verification keys are configured."
                ),
            )

        decode_kwargs: dict[str, Any] = {
            "algorithms": algorithms if algorithm in algorithms else [algorithm],
            "options": {"verify_signature": True, "verify_exp": True},
        }

        if self.settings.clerk_issuer:
            decode_kwargs["issuer"] = self.settings.clerk_issuer

        if self.settings.clerk_audience:
            decode_kwargs["audience"] = self.settings.clerk_audience
        else:
            decode_kwargs["options"]["verify_aud"] = False

        try:
            payload = jwt.decode(token, signing_key, **decode_kwargs)
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired.",
                headers={
                    "WWW-Authenticate": (
                        'Bearer error="invalid_token", '
                        'error_description="Token expired"'
                    )
                },
            ) from exc
        except jwt.InvalidIssuerError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer.",
                headers={
                    "WWW-Authenticate": (
                        'Bearer error="invalid_token", '
                        'error_description="Invalid issuer"'
                    )
                },
            ) from exc
        except jwt.InvalidAudienceError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token audience.",
                headers={
                    "WWW-Authenticate": (
                        'Bearer error="invalid_token", '
                        'error_description="Invalid audience"'
                    )
                },
            ) from exc
        except jwt.PyJWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {exc}",
                headers={
                    "WWW-Authenticate": (
                        'Bearer error="invalid_token", '
                        'error_description="Signature verification failed"'
                    )
                },
            ) from exc

        return payload


def _extract_user_from_claims(claims: dict[str, Any]) -> AuthenticatedUser:
    """Extract identity, organization, and roles from verified Clerk claims."""
    user_id = str(claims.get("sub") or "").strip()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 'sub' claim missing or empty.",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )

    roles: set[str] = set()

    # Direct role claim
    if "role" in claims and isinstance(claims["role"], str):
        roles.add(claims["role"].lower())

    # Roles list
    if "roles" in claims and isinstance(claims["roles"], list):
        for r in claims["roles"]:
            if isinstance(r, str):
                roles.add(r.lower())

    # Clerk org_role claim (e.g. 'org:admin', 'admin')
    org_role = claims.get("org_role")
    if isinstance(org_role, str):
        roles.add(org_role.lower())

    # Metadata role inspection
    metadata = claims.get("metadata") or claims.get("public_metadata") or {}
    if isinstance(metadata, dict):
        m_role = metadata.get("role")
        if isinstance(m_role, str):
            roles.add(m_role.lower())

    is_admin = bool(
        "admin" in roles
        or "org:admin" in roles
        or "administrator" in roles
        or claims.get("is_admin") is True
    )

    return AuthenticatedUser(
        user_id=user_id,
        email=claims.get("email"),
        org_id=claims.get("org_id"),
        roles=frozenset(roles),
        is_admin=is_admin,
        claims=claims,
    )


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(http_bearer_scheme)
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthenticatedUser:
    """Verify incoming Authorization: Bearer token and return AuthenticatedUser.

    Fails closed with HTTP 401 Unauthorized if missing, expired, or invalid.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    verifier = TokenVerifier(settings)
    claims = verifier.verify_token(credentials.credentials)
    return _extract_user_from_claims(claims)


async def require_admin(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> AuthenticatedUser:
    """Enforce administrative role authorization on protected endpoints.

    Raises HTTP 403 Forbidden if user is not an administrator.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required to perform this action.",
        )
    return current_user
