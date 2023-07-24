from fastapi import APIRouter, Depends, HTTPException
from models import User
from schemas import UserRequest, Token
from passlib.context import CryptContext
from starlette import status
from database import SessionLocale
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime

router = APIRouter(
    prefix = "/auth",
    tags = ["auth"]
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

SECRET_KEY = "d72bdb02e9b417a64272f303b4569df1da0a84511b55cdc79198f6c80cb3d1ce" # openssl rand -hex 32
ALGORITHM = "HS256"

# pip install "python-jose[cryptography]"
# pip install python-multipart
# pip install "passlib[bcrypt]"

def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()

    if (not user) or \
       (not bcrypt_context.verify(password, user.hashed_password)):
        return False

    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        
        if (username is None) or (user_id is None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user.")
        return {"username": username, "id": user_id, "role": user_role} 
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Could not validate user.")
    

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, 
                create_user_request: UserRequest):
    
    
    create_user_model = User(
        email_address = create_user_request.email_address,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(
                create_user_request.password
            ),
        is_active = True
    )
    
    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                    db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Could not validate user.")
    
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}
