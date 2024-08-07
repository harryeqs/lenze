# APIs built with FastAPI
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from agents.web_search_agent import WebSearchAgent
from tools.source_store import initialize_db
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

web_search_agent = WebSearchAgent(client, model='gpt-4o-mini')

initialize_db()

@app.post("/web-search", response_model=WebSearchResponseModel)
async def web_search(query: Annotated[str, Query(min_length=1, max_length=100)]) -> JSONResponse:
    agent = web_search_agent
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

    return JSONResponse(
        content={
            "answer": response,
            "related": related_queries,
            "time_taken": time_taken,
        }
    )

@app.post("/web-search-stream", response_model=WebSearchResponseModel)
async def web_search_stream(query: Annotated[str, Query(min_length=1, max_length=100)]):
    agent = web_search_agent
    agent.query = query
    start_time = time.time()

    need_search, refined_query = agent.analyze()
    if need_search:
        await agent.search(refined_query)
    
    most_relevant_sources = agent.find_sources()
    async def response_generator() -> AsyncGenerator[str, None]:
        async for chunk in agent.answer_stream(most_relevant_sources):
            yield chunk

        yield agent._format_event("--END-OF-STREAM--\n")

        related_queries = agent.interact()
        end_time = time.time()
        time_taken = f"Response generated in {end_time - start_time:.4f} seconds" 
        print(time_taken)
        
        yield agent._format_event(json.dumps({"related": related_queries, "time_taken": time_taken}))

    return StreamingResponse(response_generator(), media_type="text/event-stream")

@app.post("/image-search")
def image_search(query: str):
    pass

@app.post("/video-search")
def video_search(query: str):
    pass