from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import secrets
from ..services.auth import hash_password, verify_password
from ..storage.memory import db_users, TokenIndex
from ..core.security import TokenPayload, create_token, decode_token

router = APIRouter()
security = HTTPBearer(auto_error=False)


class UserPublic(BaseModel):
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="Email address")
    display_name: str = Field(..., description="Display name for the user")


class SignupRequest(BaseModel):
    email: EmailStr = Field(..., description="Email for signup")
    password: str = Field(..., min_length=6, description="Password with at least 6 chars")
    display_name: str = Field(..., min_length=1, description="Profile display name")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email for login")
    password: str = Field(..., description="Password")


class AuthResponse(BaseModel):
    access_token: str = Field(..., description="Bearer token")
    token_type: str = Field("bearer", description="Token type")
    user: UserPublic = Field(..., description="Logged in user")


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> UserPublic:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload: TokenPayload = decode_token(credentials.credentials)
        user = db_users.get(payload.sub)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return UserPublic(id=user["id"], email=user["email"], display_name=user["display_name"])
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post(
    "/signup",
    summary="User Signup",
    description="Create a new user account.",
    response_model=AuthResponse,
    status_code=201,
)
# PUBLIC_INTERFACE
def signup(body: SignupRequest):
    """Create a new user and return an access token."""
    # Simple uniqueness check
    for u in db_users.values():
        if u["email"].lower() == body.email.lower():
            raise HTTPException(status_code=409, detail="Email already in use")
    user_id = secrets.token_hex(8)
    db_users[user_id] = {
        "id": user_id,
        "email": str(body.email).lower(),
        "password_hash": hash_password(body.password),
        "display_name": body.display_name,
    }
    token = create_token(sub=user_id)
    TokenIndex[token] = user_id
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserPublic(id=user_id, email=body.email, display_name=body.display_name),
    )


@router.post(
    "/login",
    summary="User Login",
    description="Login with email and password to receive an access token.",
    response_model=AuthResponse,
)
# PUBLIC_INTERFACE
def login(body: LoginRequest):
    """Authenticate the user and return an access token."""
    # Find user
    user = None
    for u in db_users.values():
        if u["email"].lower() == body.email.lower():
            user = u
            break
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(sub=user["id"])
    TokenIndex[token] = user["id"]
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserPublic(id=user["id"], email=user["email"], display_name=user["display_name"]),
    )


@router.get(
    "/me",
    summary="Get Current User Profile",
    description="Retrieve the profile information for the authenticated user.",
    response_model=UserPublic,
)
# PUBLIC_INTERFACE
def me(current: UserPublic = Depends(get_current_user)):
    """Return current user's public profile."""
    return current
