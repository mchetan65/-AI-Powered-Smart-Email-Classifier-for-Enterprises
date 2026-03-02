from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class EmailRequest(BaseModel):
    content: str
    subject: Optional[str] = None
    sender: Optional[str] = None

class ClassificationResponse(BaseModel):
    category: str
    urgency: str
    confidence: float
    source: str
    xai_highlights: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    alert_flags: Optional[List[str]] = Field(default_factory=list)
    details: Optional[Dict[str, Any]] = None
