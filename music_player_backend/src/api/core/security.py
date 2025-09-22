import os
import hmac
import hashlib
import time
from dataclasses import dataclass

# NOTE: In production, prefer JWT (e.g., python-jose). Here we implement a minimal HMAC token.

DEFAULT_SECRET = "dev-secret-change-me"
TOKEN_TTL_SECONDS = 60 * 60 * 24  # 24 hours

def _secret() -> str:
    # In production, set MUSIC_BACKEND_SECRET in environment.
    return os.getenv("MUSIC_BACKEND_SECRET", DEFAULT_SECRET)

@dataclass
class TokenPayload:
    sub: str
    exp: int

# PUBLIC_INTERFACE
def create_token(sub: str) -> str:
    """Create a signed token for subject with expiry."""
    exp = int(time.time()) + TOKEN_TTL_SECONDS
    payload = f"{sub}.{exp}"
    sig = hmac.new(_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"

# PUBLIC_INTERFACE
def decode_token(token: str) -> TokenPayload:
    """Decode and validate the token. Raises ValueError on invalid token."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Malformed token")
    sub, exp_str, sig = parts
    signed = hmac.new(_secret().encode(), f"{sub}.{exp_str}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signed, sig):
        raise ValueError("Invalid signature")
    exp = int(exp_str)
    if exp < int(time.time()):
        raise ValueError("Token expired")
    return TokenPayload(sub=sub, exp=exp)
