# APIs built with FastAPI
from fastapi import FastAPI
from agents.websearch_agent import WebSearchAgent
from tools.source_store import initialize_db
from dotenv import load_dotenv
import os
from openai import OpenAI

app = FastAPI()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

web_search_agent = WebSearchAgent(client, model='gpt-4o-mini')

initialize_db()

@app.post("/web-search/{query}")
def web_search(query: str):
    response, related = web_search_agent.run(query)
    return {'response': response, 'related': related}

@app.post("/image-search/{query}")
def image_search(query: str):
    pass

@app.post("/video-search/{query}")
def video_search(query: str):
    pass