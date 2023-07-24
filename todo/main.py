from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Path
import models
from starlette import status
from pydantic import BaseModel, Field
from models import Todos
from database import engine, SessionLocale

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool = Field(default=False)

@app.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()

@app.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def read_element(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail=f"Element with id {id} not found")

@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_element(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.dict())
    db.add(todo_model)
    db.commit()

@app.put("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_element(db: db_dependency, 
                         todo_request: TodoRequest, 
                         id: int = Path(gt=0)):
    
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is None:
        return HTTPException(status_code=404, detail=f"Element with id {id} not found")
    
    # else:
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    
    db.add(todo_model)
    db.commit()

@app.delete("/todo/{id}", status_code=status.HTTP_200_OK)
async def delete_element(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is None:
        return HTTPException(status_code=404, detail=f"Element with id {id} not found")
    db.query(Todos).filter(Todos.id == id).delete()
    db.commit()
