from models import Base, Leader, LeaderRequest
from database import engine, local_session
from fastapi import FastAPI, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status

Base.metadata.create_all(bind=engine)

def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

app = FastAPI()

@app.get("/home", status_code=status.HTTP_200_OK)
def home():
    return {"this is": "home"}

@app.get("/leaders", status_code=status.HTTP_200_OK)
def get_all(db: db_dependency):
    return db.query(Leader).all()

@app.post("/leader", status_code=status.HTTP_201_CREATED)
def create_leader(db: db_dependency, new_leader: LeaderRequest):
    new_model = Leader(**new_leader.dict())
    db.add(new_model)
    db.commit()

@app.put("/leader/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_leader(db: db_dependency, 
                  leader_request: LeaderRequest, 
                  id: int = Path(gt=0)):
    leader = db.query(Leader).filter(Leader.id == id).first()
    if leader is None:
        raise HTTPException(status_code=404, detail=f"no such data with id {id} — can't update")
    else:
        leader.name = leader_request.name
        leader.country = leader_request.country
        leader.is_alive = leader_request.is_alive

        db.add(leader)
        db.commit()

@app.delete("/leader/{id}", status_code=status.HTTP_200_OK)
def delete_leader(db: db_dependency, id: int = Path(gt=0)):
    deleted = db.query(Leader).filter(Leader.id == id)
    if deleted.first() is None:
        raise HTTPException(status_code=404, detail=f"no such data with id {id} — can't delete")
    else:
        deleted.delete()
        db.commit()