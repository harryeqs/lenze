from tools.source_manager import Sources
from tools.google_search import SearchEngine
from tools.text_extraction import process_urls_async
from openai import OpenAI
from datetime import date
from .base.prompts import complete_template, ANALYZE_PROMPT, ANSWER_PROMPT, INTERACTION_PROPMT
from .base.base_agent import BaseAgent
from typing import AsyncGenerator
import numpy as np
import json
import ast
import time

__all__ = ["WebSearchAgent"]

class WebSearchAgent(BaseAgent):     
    
    def __init__(self, client: OpenAI, model: str, session_id: int, search_engine: SearchEngine):
        super().__init__(client, model, session_id, search_engine)
        self.source_manager = Sources(session_id)
        self.search_history = []

    def analyze(self):

        current_date = date.today()
        values = {'query': self.query, 'current_date': current_date, 'search_history': self.search_history}
        message = complete_template(ANALYZE_PROMPT, values)
        analysis = self._get_response(message)
        analysis = json.loads(analysis)
        need_search, refined_query = analysis["need_search"], analysis["refined_query"]
        self.refined_query = refined_query
        print(f'Need search: {need_search}')
        return need_search
  
    async def search(self, num: int = 10):

        print(f'Searching: {self.refined_query}')
        sources = self.search_engine.web_search(self.refined_query, num=num)
        urls = [source['link'] for source in sources]
        start_time = time.time()
        scraped_texts = await process_urls_async(urls)
        end_time = time.time()
        print(f'\n**Text extractions took {end_time - start_time:.4f}**')
        for i in range(len(sources)):
            sources[i]['text'] = scraped_texts[i]
        self.source_manager.store_data(sources)

    def find_sources(self):

        query_embedding = self.source_manager.generate_embedding(self.refined_query)
        most_relevant_sources = self.source_manager.find_most_relevant_sources(np.frombuffer(query_embedding, dtype=np.float32))
        return most_relevant_sources
    
    def answer(self, most_relevant_sources: list[dict]):
        
        values = {'sources': most_relevant_sources, 'query': self.refined_query}
        message = complete_template(ANSWER_PROMPT, values)
    
        print('\n=====Answer=====\n')
        response = self._get_response(message)
        self.response = response

        self.search_history.append({'query:': self.query, 'response': self.response})
        print(response)
        return self.response
    
    async def answer_stream(self, most_relevant_sources: list[dict]) -> AsyncGenerator[str, None]:
        values = {'sources': most_relevant_sources, 'query': self.query}
        message = complete_template(ANSWER_PROMPT, values)

        self.response = ""

        print('\n=====Answer=====\n')
        async for content in self._async_generator_wrapper(self._get_response_stream(message)):
            self.response += content
            print(content, end='', flush=True)
            formatted_content = content.replace('\n', '\ndata: ')
            yield self._format_event(formatted_content)

        self.search_history.append({'query:': self.query, 'response': self.response})
        print("Storing conversation")

    def interact(self):

        values = {'query': self.query, 'response': self.response}
        message = complete_template(INTERACTION_PROPMT, values)

        print('\n\n=====Related=====\n')
        related_queries = self._get_response(message)
        related = ast.literal_eval(related_queries)
        print(related)
        return related