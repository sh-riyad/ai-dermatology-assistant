from pydantic import BaseModel
from typing import List

class DoctorSearchState(BaseModel):
    task: str
    questions: List[str]
    need_input: bool
    answers: str
    nlp_query: str
    final_ans: str
