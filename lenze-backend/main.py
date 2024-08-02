# APIs built with FastAPI
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from agents.websearch_agent import WebSearchAgent
from tools.source_store import initialize_db
from dotenv import load_dotenv
from openai import OpenAI
from typing import Annotated
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

web_search_agent = WebSearchAgent(client, model='gpt-4o-mini')

initialize_db()

@app.post("/web-search", response_model=WebSearchResponseModel)
def web_search(query: Annotated[str, Query(min_length=1, max_length=100)]) -> JSONResponse:
    agent = web_search_agent
    agent.query = query
    start_time = time.time()

    need_search, refined_query = agent.analyze()
    if need_search:
        agent.search(refined_query)
    
    most_relevant_sources = agent.find_sources()
    response = agent.answer(most_relevant_sources)
    related_queries = agent.interact()

    end_time = time.time()
    time_taken = f"Response generated in {end_time - start_time:.4f} seconds"

    return JSONResponse(
        content={
            "sources": [source['link'] for source in most_relevant_sources],
            "answer": response,
            "related": related_queries,
            "time_taken": time_taken,
        }
    )

@app.get("/web-search-stream", response_model=WebSearchResponseModel)
def web_search_stream(query: Annotated[str, Query(min_length=1, max_length=100)]):
    agent = web_search_agent
    agent.query = query

    start_time = time.time()

    need_search, refined_query = agent.analyze()
    if need_search:
        agent.search(refined_query)
    
    most_relevant_sources = agent.find_sources()

    async def answer_stream():
        yield '{"sources": ' + json.dumps(most_relevant_sources) + ', "answer": "'
        response = agent.answer(most_relevant_sources)
        for chunk in response:
            yield chunk
        yield '", "related": ' + json.dumps(agent.interact()) + ', "time_taken": "'
        end_time = time.time()
        time_taken = f"Response generated in {end_time - start_time:.4f} seconds"
        yield time_taken + '"}'

    return StreamingResponse(answer_stream(), media_type="application/json")

@app.post("/image-search")
def image_search(query: str):
    pass

@app.post("/video-search")
def video_search(query: str):
    pass