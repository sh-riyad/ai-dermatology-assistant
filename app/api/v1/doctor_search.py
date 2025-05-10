from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.auth.auth import get_current_user
from app.models.users import User
from app.crud.message_crud import store_chat_message
from app.graph.doctor_search_workflow import DoctorSearchGraph
from app.schemas.doctor_search_state import DoctorSearchState
from app.schemas.chat_history import StoreMessageInput
from app.schemas.chat import ChatInput, ChatResponse


DoctorSearchRouter = APIRouter()


@DoctorSearchRouter.post("/doctor_search", response_model=ChatResponse)
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

    store_chat_message(
        StoreMessageInput(
            user_id=current_user.id,
            thread_id=input_data.thread_id,
            message_type="HumanMessage",
            message=input_data.message
        ),
        db,
    )
    
    thread = {"configurable": {"thread_id": str(input_data.thread_id)}}
    
    state = DoctorSearchGraph.get_state(thread)
    if state.next and state.next[0] == 'query_generator_and_executor':
        
        doctor_search_state = state.values
        
        if state.values['need_input']:
            doctor_search_state['answers'] = input_data.message
            doctor_search_state['need_input'] = False
            
            result = DoctorSearchGraph.invoke(doctor_search_state, thread)
        
            store_chat_message(
                StoreMessageInput(
                    user_id=current_user.id,
                    thread_id=input_data.thread_id,
                    message_type="AIMessage",
                    message=result['final_ans']
                ),
                db,
            )
            
            return ChatResponse(
                thread_id=input_data.thread_id,
                message=input_data.message,
                response=result['final_ans'],
            )

    else:

        doctor_search_state = DoctorSearchState(
            task= input_data.message,
            questions= [],
            need_input= False,
            answers= "",
            nlp_query= "",
            final_ans= "",
        )   
    
        result = DoctorSearchGraph.invoke(doctor_search_state, thread)
            
        state = DoctorSearchGraph.get_state(thread)
            
        if state.next[0] == 'query_generator_and_executor':
                
            DoctorSearchGraph.update_state(state.config, values = {"need_input": True})
            
            store_chat_message(
                StoreMessageInput(
                    user_id=current_user.id,
                    thread_id=input_data.thread_id,
                    message_type="AIMessage",
                    message=result['questions']
                ),
                db,
            )
            
            return ChatResponse(
                thread_id=input_data.thread_id,
                message=input_data.message,
                response=result['questions'],
            )
        