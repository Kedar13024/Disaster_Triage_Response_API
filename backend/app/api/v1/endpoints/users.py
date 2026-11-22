"""Routes for user registration and administrator user lookup."""

from fastapi import Depends, HTTPException, status , APIRouter
from backend.core.oauth2 import require_roles
from backend.models import models
from backend.database.database import get_db , Session
from backend.schemas.user_sch import User, User_response , UserRole
from backend.core.security import hashed_pass


router = APIRouter(prefix="/users" , tags=["Users"])

@router.post("",response_model=User_response,status_code=status.HTTP_201_CREATED,)
def create_user(user: User, db: Session = Depends(get_db)):
    """Register a user with a securely hashed password."""
    existing_user = (
        db.query(models.User)
        .filter(models.User.user_email == str(user.user_email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    new_user = models.User(
        user_fullname=user.user_fullname,
        user_phoneno=str(user.user_phoneno),
        user_email=str(user.user_email),
        user_password=hashed_pass(user.user_password),
        user_role=UserRole.CITIZEN,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{user_id}",response_model=User_response , dependencies=[Depends(require_roles(UserRole.ADMIN))])
def get_user(user_id: int , db: Session = Depends(get_db)):
    """Return a user's public profile by ID for an administrator."""

    matched_user = (
        db.query(models.User)
        .filter(
            models.User.user_id == user_id
        )
        .first()
    )

    if matched_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The user with id {user_id} doesnt't exist.",
        )

    return matched_user
