from typing import Optional
from pydantic import BaseModel, ConfigDict

class ChatInput(BaseModel):
    thread_id: int
    message: str

# Define response schema (optional but recommended)
class ChatResponse(BaseModel):
    thread_id: int
    message: str
    response: str

    model_config = ConfigDict(from_attributes=True)