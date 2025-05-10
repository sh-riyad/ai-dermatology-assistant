from sqlalchemy import asc
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.chat_history import ChatHistory
from app.schemas.chat_history import StoreMessageInput, ChatHistoryRequest

def store_chat_message(input_text: StoreMessageInput, db: Session):
    """
    Inserts a chat message into the database.
    """
    db_chat = ChatHistory(
        user_id=input_text.user_id,
        thread_id=input_text.thread_id,
        message=input_text.message,
        message_type=input_text.message_type,
    )

    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)

    return db_chat



def get_chat_history(input_text: ChatHistoryRequest, user_id: int, db: Session):
    """
    Retrieves chat history for a specific user_id (from token),
    filtered by chat_id and thread_id (from request).
    """
    query = db.query(ChatHistory).filter(ChatHistory.user_id == user_id)
    
    query = query.filter(ChatHistory.thread_id == input_text.thread_id)

    query = query.order_by(asc(ChatHistory.timestamp))
    chat_entries = query.offset(input_text.skip).limit(input_text.limit).all()

    return chat_entries
