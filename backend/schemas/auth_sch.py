from typing import Optional

from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    """Validate a user's login credentials."""

    email: EmailStr
    password: str

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    id : Optional[int] = None