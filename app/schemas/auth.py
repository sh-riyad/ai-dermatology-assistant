from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    username: str
    name: str
    email: str
    phone: str