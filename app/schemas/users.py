from typing import List, Optional
from pydantic import BaseModel

class CreateUserInput(BaseModel):
    name: str
    username: str
    email: str
    phone: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: str
    phone: str

    class Config:
        from_attributes = True

class UpdateUserInput(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None