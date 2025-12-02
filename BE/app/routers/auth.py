from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas
from app.crud import auth as auth_crud
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=auth_crud.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_crud.create_access_token(
        data={"sub": user.username or str(user.user_id)}, expires_delta=access_token_expires
    )
    user_profile = auth_crud.get_user_profile(db, user)
    return schemas.LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_profile
    )


@router.get("/me", response_model=schemas.UserProfile)
async def read_users_me(current_user=Depends(auth_crud.get_current_active_user), db: Session = Depends(get_db)):
    return auth_crud.get_user_profile(db, current_user)


@router.post("/logout")
async def logout() -> dict:
    # Stateless JWT logout; frontend should discard the token.
    return {"message": "Logged out successfully"}

