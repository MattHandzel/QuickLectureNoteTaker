from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str
    language: Optional[str] = None

class SessionMeta(BaseModel):
    session_id: str
    source: str
    created: datetime = Field(default_factory=datetime.utcnow)
    duration: Optional[float] = None
    transcript_model: Optional[str] = None
    llm_model: Optional[str] = None

class Transcript(BaseModel):
    segments: List[TranscriptSegment]
    language: Optional[str] = None
