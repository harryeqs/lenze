from agents.web_search_agent import WebSearchAgent
from tools.source_store import initialize_db
import os
from openai import OpenAI
import asyncio

initialize_db()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
web_search = WebSearchAgent(client, model='gpt-4o-mini')
query = input("Please input your query: ")
asyncio.run(web_search.run(query))