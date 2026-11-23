"""Authentication routes for exchanging credentials for access tokens."""

from fastapi import Depends, HTTPException, status , APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from backend.core.oauth2 import create_access_token
from backend.models import models
from backend.database.database import get_db , Session
from backend.core.security import verify_pass
from backend.schemas.auth_sch import Token


router = APIRouter(prefix="/login" , tags=["Authentication"])

@router.post("/" , response_model= Token)
def login(creds : OAuth2PasswordRequestForm = Depends() , db : Session = Depends(get_db)):
    """Verify submitted credentials and return a signed bearer token."""

    existing_user = db.query(models.User).filter(models.User.user_email == creds.username).first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail="Invalid credentials!")

    if existing_user:
        if not verify_pass(creds.password , existing_user.user_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail="Invalid credentials!")

    access_token = create_access_token(data={"user_id":existing_user.user_id})

    return {"access_token" : access_token , "token_type" :"bearer" , "role": existing_user.user_role}
