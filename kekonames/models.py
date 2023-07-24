from database import Base
from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel, Field

class Leader(Base):
    __tablename__ = "commleads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    country = Column(String)
    is_alive = Column(Boolean, default=False)

class LeaderRequest(BaseModel):
    
    name: str = Field(min_length=1, max_length=50)
    country: str = Field(min_length=1, max_length=50)
    is_alive: bool = Field(default=False)
    
    class Config:
        orm_mode = True
        # schema_extra = {
        #     "example": {
        #         "name": "politician's name",
        #         "country": "where s/he from",
        #         "is_alive": "true or false"
        #     }
        # }