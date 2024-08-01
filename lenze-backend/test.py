from agents.websearch_agent import WebSearchAgent
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
web_search = WebSearchAgent(client, model='gpt-4o-mini')
query = input("Please input your query: ")
web_search.run(query)