from fastapi import APIRouter, Depends, HTTPException, status
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.auth.auth import get_current_user
from app.models.users import User
from app.crud.message_crud import store_chat_message, get_chat_history

from app.schemas.chat_history import (
    ChatHistoryRequest,
    ChatHistoryResponse,
    StoreMessageInput
)
from app.schemas.chat import ChatInput, ChatResponse


ChatRouter = APIRouter()


@ChatRouter.post("/chat", response_model=ChatResponse)
def chat(input_data: ChatInput, current_user: User = Depends(get_current_user),db: Session = Depends(get_db),):
    """
    Chat endpoint that processes user input using the ChatOpenAI model and
    stores messages (human & AI) in the database.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )

    llm = ChatOpenAI(model="gpt-4o")

    response = llm.invoke(input_data.message)
    
    print(response)

    store_chat_message(
        StoreMessageInput(
            user_id=current_user.id,
            thread_id=input_data.thread_id,
            message_type="HumanMessage",
            message=input_data.message
        ),
        db,
    )

    store_chat_message(
        StoreMessageInput(
            user_id=current_user.id,
            thread_id=input_data.thread_id,
            message_type="AIMessage",
            message=response.content
        ),
        db,
    )

    return ChatResponse(
        thread_id=input_data.thread_id,
        message=input_data.message,
        response=response.content,
    )


@ChatRouter.get("/chat/history", response_model=ChatHistoryResponse)
def fetch_chat_history(query_params: ChatHistoryRequest = Depends(),current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    """
    Endpoint to retrieve chat history for the current user,
    filtered by chat_id, thread_id, skip, and limit.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )

    # user_id is derived from the token (current_user)
    chat_entries = get_chat_history(query_params, user_id=current_user.id, db=db)
    # Return a structured response using Pydantic
    return ChatHistoryResponse(chat_history=chat_entries)