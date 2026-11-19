"""Pydantic schemas for login credentials and authentication tokens."""

from typing import Optional

from pydantic import BaseModel, EmailStr

from backend.schemas.user_sch import UserRole


class UserLogin(BaseModel):
    """Validate a user's login credentials."""

    email: EmailStr
    password: str

class Token(BaseModel):
    """Represent an access token returned after successful login."""
    access_token : str
    token_type : str
    role : UserRole

class TokenData(BaseModel):
    """Hold the user identifier decoded from an access token."""
    id : Optional[int] = None
