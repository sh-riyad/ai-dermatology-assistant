from pydantic import BaseModel, ConfigDict
from typing import Optional, List

    
class StoreMessageInput(BaseModel):
    user_id: int
    thread_id: int
    message: str
    message_type: str

    model_config = ConfigDict(from_attributes=True)


class ChatHistoryRequest(BaseModel):
    thread_id: int
    skip: int = 0
    limit: int = 10

class ChatHistoryItem(BaseModel):
    # Include all the fields you want to expose
    id: int
    user_id: int
    thread_id: Optional[int]
    message: str
    message_type: str

    model_config = ConfigDict(from_attributes=True)
    
class ChatHistoryResponse(BaseModel):
    chat_history : List[ChatHistoryItem]