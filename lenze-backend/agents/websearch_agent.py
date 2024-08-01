from tools.google_search import google_scrape_search, get_urls
from tools.source_store import local_store, local_read, generate_embedding, find_most_relevant_sources
from tools.text_extraction import process_urls
from datetime import date
from .base.prompts import complete_template, ANALYZE_PROMPT, ANSWER_PROMPT, INTERACTION_PROPMT
from .base.base_agent import BaseAgent
import numpy as np
import time
import json

__all__ = ["WebSearchAgent"]

class WebSearchAgent(BaseAgent):     

    def analyze(self):
        current_date = date.today()
        values = {'query': self.query, 'current_date': current_date, 'search_history': self.search_history}
        message = complete_template(ANALYZE_PROMPT, values)
        analysis = self._get_response(message, stream=False)
        analysis = json.loads(analysis)
        need_search, refined_query = analysis["need_search"], analysis["refined_query"]
        return need_search, refined_query
  
    def search(self, refiend_query: str):

        sources = []
        urls = get_urls(google_scrape_search(refiend_query))
        urls = list(set(urls))

        scraped_texts = process_urls(urls)
        sources = [{'link': url, 'text': text} for url, text in zip(urls, scraped_texts)]
        
        local_store(sources)

    def answer(self):

        query_embedding = generate_embedding(self.query)
        sources = local_read()
        most_relevant_sources = find_most_relevant_sources(np.frombuffer(query_embedding, dtype=np.float32), sources)
        values = {'sources': most_relevant_sources, 'query': self.query}
        message = complete_template(ANSWER_PROMPT, values)
    
        print('\n=====Answer=====\n')
        response = self._get_response(message)
        self.response = response

        self.search_history.append({'query:': self.query, 'response': self.response})
        return self.response

    def interact(self):

        values = {'query': self.query, 'response': self.response}
        message = complete_template(INTERACTION_PROPMT, values)

        print('\n\n=====Related=====\n')
        related_queries = self._get_response(message)
        return related_queries

    def run(self, query):

            self.query = query
            start_time = time.time()
                
            need_search, refined_query = self.analyze()
                
            if need_search:
                self.search(refined_query)
            
            response, related = self.answer(), self.interact()

            end_time = time.time()
            time_taken = f'**Response generated in {end_time-start_time:.4f} seconds**'
            print(f'\n{time_taken}\n')

            return response, related
        