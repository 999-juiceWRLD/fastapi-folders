from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Todos, User
from database import SessionLocale
from .auth import get_current_user

# pip install psycopg2-binary -> for postgresql
# pip install pymsql -> for mysql


router = APIRouter(
    prefix="/admin",
    tags=["admin page"]
)

def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todo", status_code=status.HTTP_200_OK)
def get_all_todos(user: user_dependency, db: db_dependency):
    if user is None or user["role"] != "admin":
        raise HTTPException(status_code=401, detail="you're not admin")
    
    return db.query(Todos).all()


@router.get("/subs", status_code=status.HTTP_200_OK)
def get_all_todos(user: user_dependency, db: db_dependency):
    if user is None or user["role"] != "admin":
        raise HTTPException(status_code=401, detail="you're not admin")

    return db.query(User).all()


@router.delete("/todo/{id}", status_code=status.HTTP_200_OK)
def delete_user(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None or user["role"] != "admin":
        raise HTTPException(status_code=401, detail="you're not admin")
    
    todo_model = db.query(Todos).filter(id == Todos.id).first()
    if todo_model is None:
        return HTTPException(status_code=404, detail="no such content is found")
    
    db.query(Todos).filter(Todos.id == id).delete()
    db.commit()
    