from pydantic import BaseModel
import markdown
import pytz
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.datetime.now(pytz.timezone('Europe/London')))
    sources = Column(String, nullable=True)

class SearchHistory(Base):
    __tablename__ = "searches"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    query = Column(Text, index=True)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.now())
    
    session = relationship("Session", back_populates="searches")

Session.searches = relationship("SearchHistory", order_by=SearchHistory.id, back_populates="session")

def WebSearchResponseModel(BaseModel):
    id: int | None = None
    time_taken: str
    sources: list[dict]
    answer: markdown.Markdown | str
    related: list[str]

def ConversationInfo(BaseModel):
    query: str
    response: str

def SessionInfo(BaseModel):
    session_id: int
    start_time: datetime.datetime | str
    first_query: str
