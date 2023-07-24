from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Todos, User
from schemas import UserVerification
from database import SessionLocale
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/me", status_code=status.HTTP_200_OK)
def about_me(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=404, detail="login first")
    about_me = db.query(User).filter(user["id"] == User.id).first()
    return about_me
    

@router.put("/me", status_code=status.HTTP_204_NO_CONTENT)
def change_password(user: user_dependency, db: db_dependency, 
                    user_verification: UserVerification):
    
    if user_verification.new_password != user_verification.new_password_again:
        raise HTTPException(404, detail="new passwords don't match")
    
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    
    user_model = db.query(User).filter(user["id"] == User.id).first()
    if not bcrypt_context.verify(user_verification.old_password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="you entered your old password wrong")
    
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()