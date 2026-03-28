from pydantic import BaseModel
from typing import Optional, List

class PersonaRequest(BaseModel):
    sample_texts: List[str]
    tone: str
    risk_level: str
    communication_style: str
    personality_type: str
    additional_traits: Optional[str] = ""

class ReplyRequest(BaseModel):
    session_id: str
    original_message: str
    context: Optional[str] = ""

class DecisionRequest(BaseModel):
    session_id: str
    situation: str
    options: List[str]
    constraints: Optional[str] = ""

class PlanRequest(BaseModel):
    session_id: str
    goal: str
    timeframe: str
    priorities: Optional[List[str]] = []