from typing import Optional

from pydantic import BaseModel, EmailStr

from backend.schemas.user_sch import UserRole


class UserLogin(BaseModel):
    """Validate a user's login credentials."""

    email: EmailStr
    password: str

class Token(BaseModel):
    access_token : str
    token_type : str
    role : UserRole

class TokenData(BaseModel):
    id : Optional[int] = None