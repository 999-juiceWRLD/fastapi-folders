from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    email_address: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str
    

class UserVerification(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)
    new_password_again: str = Field(min_length=6)


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool = Field(default=False)


class Token(BaseModel):
    access_token: str
    token_type: str
