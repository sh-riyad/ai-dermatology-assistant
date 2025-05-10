from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.auth.auth import get_current_user
from app.models.users import User
from app.crud.message_crud import store_chat_message
from app.graph.disease_report_workflow import disease_report_graph
from app.schemas.disease_report_state import ReportState
from app.schemas.chat_history import StoreMessageInput
from app.schemas.chat import ChatInput, ChatResponse


DiseaseReportRouter = APIRouter()


@DiseaseReportRouter.post("/disease-report", response_model=ChatResponse)
def chat(input_data: ChatInput, current_user: User = Depends(get_current_user),db: Session = Depends(get_db),):

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )

    report_state = ReportState(
        task=input_data.message,
        plan=None,
        draft=None,
        critique=None,
        content=None,
        revision_number=0,
        max_revisions=3, 
        detail_level="detailed",
        language_preference="en",
        disclaimers="This information is for educational purposes and not a substitute for professional medical advice."
    )
    
    thread = {"configurable": {"thread_id": input_data.thread_id}}

    result_states = []
    for s in disease_report_graph.stream(report_state, thread):
        result_states.append(s)


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
            message=result_states[-1]['generate']['draft']
        ),
        db,
    )

    return ChatResponse(
        thread_id=input_data.thread_id,
        message=input_data.message,
        response=result_states[-1]['generate']['draft'],
    )

