import os
import hashlib
import secrets

def _salt() -> str:
    # In production, use a strong KDF like bcrypt/argon2.
    return os.getenv("MUSIC_BACKEND_SALT", "dev-salt")

# PUBLIC_INTERFACE
def hash_password(password: str) -> str:
    """Hash a password using SHA256 with app salt and per-password random pepper."""
    pepper = secrets.token_hex(8)
    digest = hashlib.sha256(f"{_salt()}::{password}::{pepper}".encode()).hexdigest()
    return f"{pepper}${digest}"

# PUBLIC_INTERFACE
def verify_password(password: str, stored: str) -> bool:
    """Verify password against stored hash."""
    try:
        pepper, digest = stored.split("$", 1)
        calc = hashlib.sha256(f"{_salt()}::{password}::{pepper}".encode()).hexdigest()
        return secrets.compare_digest(calc, digest)
    except Exception:
        return False
