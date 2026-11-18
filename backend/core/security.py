"""Password hashing and verification utilities."""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashed_pass(password: str) -> str:
    """Return a bcrypt hash of a plain-text password."""
    return pwd_context.hash(password)


def verify_pass(password: str, hashedPassword: str) -> bool:
    """Check a plain-text password against its stored hash."""
    return pwd_context.verify(password, hashedPassword)
