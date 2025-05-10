from pydantic import BaseModel
from typing import List, Dict, Optional


class ReportState(BaseModel):
    task: str
    plan: Optional[str]
    draft: Optional[str]
    critique: Optional[str]
    content: Optional[List[str]]
    revision_number: Optional[int]
    max_revisions: Optional[int]

    detail_level: Optional[str]
    language_preference: Optional[str]
    disclaimers: Optional[str]


class Queries(BaseModel):
    queries: List[str]