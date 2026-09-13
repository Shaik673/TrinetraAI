"""
Authentication API routes — local JWT auth + social OAuth (Google, GitHub, Facebook).
"""
import secrets
import string
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import decode_token, oauth2_scheme
from app.db.base import get_db
from app.schemas.auth import (
    PasswordResetRequest,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger("auth_routes")

# ---------------------------------------------------------------------------
# OAuth provider configuration
# ---------------------------------------------------------------------------

OAUTH_PROVIDERS = {
    "google": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
        "client_id_key": "GOOGLE_CLIENT_ID",
        "client_secret_key": "GOOGLE_CLIENT_SECRET",
        "scope": "openid email profile",
    },
    "github": {
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "client_id_key": "GITHUB_CLIENT_ID",
        "client_secret_key": "GITHUB_CLIENT_SECRET",
        "scope": "read:user user:email",
    },
    "facebook": {
        "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "userinfo_url": "https://graph.facebook.com/me?fields=id,name,email,picture",
        "client_id_key": "FACEBOOK_CLIENT_ID",
        "client_secret_key": "FACEBOOK_CLIENT_SECRET",
        "scope": "email public_profile",
    },
}


def _get_provider_config(provider: str) -> dict:
    """Return OAuth config for a named provider, raising 400 for unknowns."""
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}. Supported: {list(OAUTH_PROVIDERS.keys())}",
        )
    return OAUTH_PROVIDERS[provider]


def _get_client_credentials(provider: str) -> tuple[str, str]:
    """Return (client_id, client_secret) for a provider from settings."""
    cfg = _get_provider_config(provider)
    client_id = getattr(settings, cfg["client_id_key"], "")
    client_secret = getattr(settings, cfg["client_secret_key"], "")
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"{provider.title()} OAuth credentials not configured. "
                   f"Add {cfg['client_id_key']} and {cfg['client_secret_key']} to your .env file.",
        )
    return client_id, client_secret


def _callback_url(provider: str) -> str:
    return f"{settings.API_V1_PREFIX}/auth/oauth/{provider}/callback"


def _frontend_error_redirect(error: str) -> RedirectResponse:
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error={error}")


# ---------------------------------------------------------------------------
# Standard (local) auth endpoints
# ---------------------------------------------------------------------------

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    tokens = auth_service.create_tokens(user)
    return {**tokens, "user": user}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = await auth_service.get_current_user(db, body.refresh_token)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    tokens = auth_service.create_tokens(user)
    return {**tokens, "user": user}


@router.post("/request-password-reset")
async def request_password_reset(body: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """Accept password-reset requests without revealing whether an account exists.

    Email delivery is intentionally an infrastructure concern and can be added
    behind this endpoint without changing the browser contract.
    """
    user = await auth_service.get_user_by_email(db, body.email)
    if user:
        logger.info("password_reset_requested", user_id=str(user.id))
    return {"message": "If an account matches that email, reset instructions will be sent."}


async def get_authenticated_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """Return the user represented by a valid access token."""
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    user = await auth_service.get_current_user(db, token)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_authenticated_user)):
    return user


@router.put("/me", response_model=UserResponse)
async def update_me(profile: UserUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_authenticated_user)):
    return await auth_service.update_user(db, user, **profile.model_dump(exclude_unset=True))


# ---------------------------------------------------------------------------
# Social OAuth endpoints
# ---------------------------------------------------------------------------

@router.get("/oauth/{provider}", summary="Initiate OAuth login flow")
async def oauth_redirect(provider: str):
    """Redirect the browser to the social provider's authorization page."""
    cfg = _get_provider_config(provider)
    client_id, _ = _get_client_credentials(provider)

    # Build redirect URI pointing back to our callback
    redirect_uri = f"{settings.FRONTEND_URL.rstrip('/')}/auth/callback"

    # State param to prevent CSRF (simple random token stored in frontend URL)
    state = secrets.token_urlsafe(16)

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": cfg["scope"],
        "response_type": "code",
        "state": f"{provider}:{state}",
    }

    # Provider-specific extras
    if provider == "google":
        params["access_type"] = "online"
        params["prompt"] = "select_account"

    from urllib.parse import urlencode
    auth_url = f"{cfg['auth_url']}?{urlencode(params)}"
    logger.info("oauth_redirect", provider=provider)
    return RedirectResponse(url=auth_url)


@router.get("/oauth/{provider}/callback", summary="OAuth provider callback")
async def oauth_callback(
    provider: str,
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Exchange authorization code for user profile, upsert user, return JWT via redirect."""
    if error:
        logger.warning("oauth_provider_error", provider=provider, error=error)
        return _frontend_error_redirect(f"provider_denied_{provider}")

    if not code:
        return _frontend_error_redirect("missing_code")

    cfg = _get_provider_config(provider)
    client_id, client_secret = _get_client_credentials(provider)
    redirect_uri = f"{settings.FRONTEND_URL.rstrip('/')}/auth/callback"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # ----------------------------------------------------------------
            # 1. Exchange code → access token
            # ----------------------------------------------------------------
            token_params = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }

            if provider == "github":
                # GitHub returns form-encoded; needs Accept header
                token_resp = await client.post(
                    cfg["token_url"],
                    data=token_params,
                    headers={"Accept": "application/json"},
                )
            else:
                token_resp = await client.post(cfg["token_url"], data=token_params)

            if token_resp.status_code != 200:
                logger.error("oauth_token_exchange_failed", provider=provider, status=token_resp.status_code)
                return _frontend_error_redirect("token_exchange_failed")

            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                return _frontend_error_redirect("no_access_token")

            # ----------------------------------------------------------------
            # 2. Fetch user profile from provider
            # ----------------------------------------------------------------
            userinfo_resp = await client.get(
                cfg["userinfo_url"],
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if userinfo_resp.status_code != 200:
                return _frontend_error_redirect("userinfo_failed")

            profile = userinfo_resp.json()

            # ----------------------------------------------------------------
            # 3. Normalize profile fields across providers
            # ----------------------------------------------------------------
            if provider == "google":
                provider_id = profile.get("sub")
                email = profile.get("email")
                full_name = profile.get("name")
                avatar_url = profile.get("picture")

            elif provider == "github":
                provider_id = str(profile.get("id"))
                email = profile.get("email")
                # GitHub may not expose primary email; fetch separately
                if not email:
                    emails_resp = await client.get(
                        "https://api.github.com/user/emails",
                        headers={"Authorization": f"Bearer {access_token}"},
                    )
                    if emails_resp.status_code == 200:
                        emails = emails_resp.json()
                        primary = next((e for e in emails if e.get("primary") and e.get("verified")), None)
                        email = primary["email"] if primary else None
                full_name = profile.get("name") or profile.get("login")
                avatar_url = profile.get("avatar_url")

            elif provider == "facebook":
                provider_id = str(profile.get("id"))
                email = profile.get("email")
                full_name = profile.get("name")
                avatar_url = profile.get("picture", {}).get("data", {}).get("url")

            else:
                return _frontend_error_redirect("unknown_provider")

            if not email or not provider_id:
                return _frontend_error_redirect("missing_email_or_id")

    except httpx.RequestError as exc:
        logger.error("oauth_http_error", provider=provider, error=str(exc))
        return _frontend_error_redirect("network_error")

    # ----------------------------------------------------------------
    # 4. Upsert user in database
    # ----------------------------------------------------------------
    try:
        user = await auth_service.find_or_create_oauth_user(
            db,
            provider=provider,
            provider_id=provider_id,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
        )
    except Exception as exc:
        logger.error("oauth_upsert_failed", provider=provider, error=str(exc))
        return _frontend_error_redirect("account_error")

    # ----------------------------------------------------------------
    # 5. Issue JWT and redirect frontend
    # ----------------------------------------------------------------
    tokens = auth_service.create_tokens(user)
    access = tokens["access_token"]
    refresh = tokens["refresh_token"]

    # Redirect back to frontend callback page with tokens as query params
    redirect_url = (
        f"{settings.FRONTEND_URL.rstrip('/')}/auth/callback"
        f"?access_token={access}&refresh_token={refresh}&provider={provider}"
    )
    logger.info("oauth_login_success", provider=provider, user_id=str(user.id))
    return RedirectResponse(url=redirect_url)
