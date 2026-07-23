from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class TriageStartRequest(BaseModel):
    complaint: str

class TriageAnswerRequest(BaseModel):
    feature_name: str
    feature_value: Any  # Can be float for numbers or string for categories like pain_type

class TriageChatResponse(BaseModel):
    session_id: int
    status: str
    matched_template: Optional[str] = None
    confidence: Optional[float] = None
    next_question_feature: Optional[str] = None
    message: str

class TriageVectorResponse(BaseModel):
    session_id: int
    user_id: int
    vector: List[Any]
    feature_names: List[str]
    message: str
