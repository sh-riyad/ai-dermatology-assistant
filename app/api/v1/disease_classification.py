from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.auth.auth import get_current_user
from app.models.users import User
from app.crud.message_crud import store_chat_message
from app.graph.classification_workflow import ClassificationGraph
from app.schemas.classification_state import ClassificationState
from app.schemas.chat_history import StoreMessageInput
from app.schemas.chat import ChatInput, ChatResponse
import base64
from typing import Optional


ClassificationRouter = APIRouter()



@ClassificationRouter.post("/classification", response_model=ChatResponse)
async def chat(thread_id: int = Form(...),
               message: str = Form(...),
               uploaded_file: Optional[UploadFile] = File(None),
               current_user: User = Depends(get_current_user),
               db: Session = Depends(get_db)
               ):
    """
    Chat endpoint that processes user input using the ChatOpenAI model and
    stores messages (human & AI) in the database.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )

    if uploaded_file:
        if not uploaded_file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is not an image."
            )

        img_bytes = await uploaded_file.read()

        base64_image = base64.b64encode(img_bytes).decode("utf-8")
    else:
        base64_image=""
            
            
    store_chat_message(
        StoreMessageInput(
            user_id=current_user.id,
            thread_id=thread_id,
            message_type="HumanMessage",
            message=message
        ),
        db,
    )
    
    thread = {"configurable": {"thread_id": str(thread_id)}}
    
    state = ClassificationGraph.get_state(thread)
    
    if state.next and state.next[0] == 'hypothesis_updater':
                
        if state.values.get('need_input', False):
            ClassificationGraph.update_state(state.config, values={"user_responses": message})

            result = ClassificationGraph.invoke(None, thread)
        
            if result.get('final_ans'):
                store_chat_message(
                    StoreMessageInput(
                        user_id=current_user.id,
                        thread_id=thread_id,
                        message_type="AIMessage",
                        message=result['final_ans']
                    ),
                    db,
                )
                ClassificationGraph.update_state(state.config, values={"need_input": False})
                return ChatResponse(
                    thread_id=thread_id,
                    message=message,
                    response=result['final_ans'],
                ) 
            else:
                store_chat_message(
                    StoreMessageInput(
                        user_id=current_user.id,
                        thread_id=thread_id,
                        message_type="AIMessage",
                        message=result['current_question']
                    ),
                    db,
                )
                ClassificationGraph.update_state(state.config, values={"need_input": True})
                return ChatResponse(
                    thread_id=thread_id,
                    message=message,
                    response=result['current_question'],
                )
        

    else:
        
        classification_state = ClassificationState(
            conversation_history= [],
            current_hypotheses= [],
            research_findings= {},
            research_queries= [],
            user_responses= "",
            iteration_count= 0,
            input_description= message,
            encoded_image=base64_image,
            image_details="",
            confident=False,
            current_question="",
            need_input=False,
            final_ans="",
        )    
    
        result = ClassificationGraph.invoke(classification_state, thread)
            
        state = ClassificationGraph.get_state(thread)
        
        if state.next[0] == 'hypothesis_updater':
                
            ClassificationGraph.update_state(state.config, values = {"need_input": True})
            
            store_chat_message(
                StoreMessageInput(
                    user_id=current_user.id,
                    thread_id=thread_id,
                    message_type="AIMessage",
                    message=result['current_question']
                ),
                db,
            )
            
            return ChatResponse(
                thread_id=thread_id,
                message=message,
                response=result['current_question'],
            )
        