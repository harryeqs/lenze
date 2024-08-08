from pydantic import BaseModel
import markdown
import pytz
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

DATABASE_URL = "sqlite:///./data/search_history.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

def initialize_session():
    Base.metadata.create_all(bind=engine)


def ResponseModel(BaseModel):
    id: int | None = None
    time_taken: str

def WebSearchResponseModel(ResponseModel):
    sources: list[dict]
    answer: markdown.Markdown | str
    related: list[str]

def ImageSearchResponseModel(ResponseModel):
    pass

def VideoSearchResponseModel(ResponseModel):
    pass