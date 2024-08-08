# APIs built with FastAPI
from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from agents.web_search_agent import WebSearchAgent
from tools.sources import Sources
from sqlalchemy.orm import Session
from models import SearchHistory, Session as DBSession, initialize_session, SessionLocal
from openai import OpenAI
from typing import Annotated, AsyncGenerator
from models import WebSearchResponseModel
import os
import time
import json

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",  # Adjust based on your frontend URL
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

initialize_session()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/start-session")
def start_session(db: Session = Depends(get_db)):
    new_session = DBSession()
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    sources = Sources(new_session.id)
    new_session.sources = sources.table_name
    print(new_session.sources)
    return {"session_id": new_session.id, "start_time": new_session.start_time, "sources": new_session.sources}

@app.get("/search-history")
def get_search_history(db: Session = Depends(get_db)):
    sessions = db.query(DBSession).all()
    session_histories = []
    for session in sessions:
        first_query = db.query(SearchHistory).filter(SearchHistory.session_id == session.id).order_by(SearchHistory.timestamp).first()
        if first_query:
            session_histories.append({
                "session_id": session.id,
                "start_time": session.start_time,
                "first_query": first_query.query
            })
    return JSONResponse(content=session_histories)

@app.post("/web-search/{session_id}", response_model=WebSearchResponseModel)
async def web_search(session_id: int, query: Annotated[str, Query(min_length=1, max_length=100)], db: Session = Depends(get_db)) -> JSONResponse:
    agent = WebSearchAgent(client, 'gpt-4o-mini', session_id)
    agent.query = query
    start_time = time.time()

    need_search, refined_query = agent.analyze()
    if need_search:
        await agent.search(refined_query)
    
    most_relevant_sources = agent.find_sources()
    response = agent.answer(most_relevant_sources)
    related_queries = agent.interact()

    end_time = time.time()
    time_taken = f"Response generated in {end_time - start_time:.4f} seconds"

    search_entry = SearchHistory(session_id=session_id, query=query, response=response)
    db.add(search_entry)
    db.commit()
    db.refresh(search_entry)

    return JSONResponse(
        content={
            "answer": response,
            "related": related_queries,
            "time_taken": time_taken,
        }
    )

@app.post("/web-search-stream/{session_id}", response_model=WebSearchResponseModel)
async def web_search_stream(session_id: int, query: Annotated[str, Query(min_length=1, max_length=100)], db: Session = Depends(get_db)):
    agent = WebSearchAgent(client, 'gpt-4o-mini', session_id)
    agent.query = query
    start_time = time.time()

    need_search, refined_query = agent.analyze()
    if need_search:
        await agent.search(refined_query)
    
    most_relevant_sources = agent.find_sources()
    async def response_generator() -> AsyncGenerator[str, None]:
        async for chunk in agent.answer_stream(most_relevant_sources):
            yield chunk
            
        related_queries = agent.interact()
        end_time = time.time()
        time_taken = f"Response generated in {end_time - start_time:.4f} seconds" 
        print(time_taken)
        
        final_json = json.dumps({"related": related_queries, "time_taken": time_taken})
        yield f'event: finaljson\ndata: {final_json}\n\n'
    
    search_entry = SearchHistory(session_id=session_id, query=query, response=agent.answer(most_relevant_sources))
    db.add(search_entry)
    db.commit()
    db.refresh(search_entry)

    return StreamingResponse(response_generator(), media_type="text/event-stream")