from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid

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

class NoteType(str, Enum):
    Definition = "Definition"
    Concept = "Concept"
    Theorem = "Theorem"
    Procedure = "Procedure"
    Example = "Example"
    Equation = "Equation"
    Pitfall = "Pitfall"
    QA = "QA"
    Term = "Term"

class AtomicNote(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    type: NoteType
    title: str
    body: str
    timestamp: str
    span: List[str]
    importance: int = 1
    tags: List[str] = []
    image_path: Optional[str] = None
