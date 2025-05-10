from typing import List, Dict, Tuple, Union, Optional
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

class ClassificationState(BaseModel):
    conversation_history: List[Union[HumanMessage, AIMessage, SystemMessage]]
    current_hypotheses: List[Tuple[str, float]]
    research_findings: Dict[str, str]
    research_queries: List[str]
    user_responses: str
    encoded_image: Optional[str] = None
    image_details: Optional[str] = None
    iteration_count: int
    input_description: str
    confident: bool
    current_question: str
    need_input: bool
    final_ans:str

    class Config:
        arbitrary_types_allowed = True
