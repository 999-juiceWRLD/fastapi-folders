from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from schemas import TodoRequest
from models import Todos
from database import SessionLocale
from .auth import get_current_user

router = APIRouter(
    prefix = "/api",
    tags = ["main"]
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
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthenticated. Sign in/up first.")
    return db.query(Todos).filter(user["id"] == Todos.owner_id).all()



@router.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def read_element(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthenticated. Sign in/up first.")
    todo_model = db.query(Todos).filter(Todos.id == id) \
                    .filter(Todos.owner_id == user["id"])   \
                    .first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail=f"Element with id {id} not found")



@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_post(user: user_dependency, 
                      db: db_dependency, 
                      todo_request: TodoRequest):
    
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthenticated. Sign in/up first.")
    
    todo_model = Todos(**todo_request.dict(), owner_id=user["id"])
    db.add(todo_model)
    db.commit()



@router.put("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_element(user: user_dependency, db: db_dependency, 
                         todo_request: TodoRequest, 
                         id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthenticated. Sign in/up first.")
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    """
    todo_model = db.query(Todos)                            \
                    .filter(user["id"] == Todos.owner_id)   \
                    .filter(Todos.id == id)                 \
                    .first()
    """
    if todo_model is None:
        return HTTPException(status_code=404, detail=f"Element with id {id} not found")
    if todo_model.owner_id != user["id"]:
        raise HTTPException(status_code=403, detail="You are not the owner of this todo record")
    
    # else:
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    
    db.add(todo_model)
    db.commit()



@router.delete("/todo/{id}", status_code=status.HTTP_200_OK)
async def delete_element(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthenticated. Sign in/up first.")
    
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model.owner_id != user["id"]:
        raise HTTPException(status_code=403, detail="You are not the owner of this todo record")
    if todo_model is None:
        return HTTPException(status_code=404, detail=f"Element with id {id} not found")
    db.query(Todos).filter(Todos.id == id).delete()
    db.commit()
