"""JWT creation, authentication dependencies, and role authorization."""

from datetime import datetime, timedelta , timezone
from fastapi import Depends, HTTPException , status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt , JWTError
from sqlalchemy.orm import Session
from backend.core.config import get_settings
from backend.database.database import get_db
from backend.models.models import User
from backend.schemas.auth_sch import Token, TokenData
from backend.schemas.user_sch import UserRole


settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def create_access_token(data : dict):
    """Encode token claims with an expiration using configured JWT settings."""

    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)

    payload.update({"exp":expire})

    return jwt.encode(payload,settings.secret_key,algorithm=settings.algorithm)

def verify_access_token(token : Token , cred_exception):
    """Decode a bearer token and return its user ID or raise the credential error."""

    try:
        payload = jwt.decode(token,settings.secret_key,algorithms=[settings.algorithm])
        id : str = payload.get("user_id")

        if id is None:
            raise cred_exception

        tokenData = TokenData(id=id)

    except JWTError:
        raise cred_exception

    return tokenData


def get_current_user(token : str = Depends(oauth2_scheme) , db : Session = Depends(get_db)):
    """Resolve the authenticated user from the bearer token and database."""

    cred_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token", headers={"WWW-Authenticate":"Bearer"})

    token = verify_access_token(token , cred_exception)

    current_user = db.query(User).filter(User.user_id == token.id).first()

    if current_user is None:
        raise cred_exception

    return current_user


def require_roles(*allowed_roles : UserRole):
    """Allow an endpoint only to users with one of the listed roles."""
    def role_checker(current_user = Depends(get_current_user)):
        """Reject the request unless the authenticated user has an allowed role."""
        if current_user.user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return role_checker
