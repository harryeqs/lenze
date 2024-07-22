from openai import OpenAI
from tools.google_scrape_search import google_scrape_search, get_urls
from tools.google_api_search import google_api_search
from tools.source_store import local_store, local_read, initialize_db, generate_embedding, find_most_relevant_sources
from tools.web_scraper import scrape_urls
from datetime import date, datetime
from prompts import ANALYZE_PROMPT, OPT_PROMPT, ANSWER_PROMPT, INTERACTION_PROPMT
import numpy as np
import os
import time
import logging
import ast

__all__ = ["Lenze"]

def complete_prompt(template, values):
    """
    Fill placeholders in the template with corresponding values from the dictionary to complete prompt.

    :param template: List of dictionaries representing the prompt template.
    :param values: Dictionary containing placeholder names and their corresponding values.

    :return: List of dictionaries with placeholders filled.
    """
    filled_template = []

    for part in template:
        filled_content = part["content"]
        for placeholder, value in values.items():
            filled_content = filled_content.replace(f'{{{placeholder}}}', str(value))
        filled_template.append({"role": part["role"], "content": filled_content})

    return filled_template

class Lenze:
    def __init__(self, client: OpenAI, model: str, mode: str="default"):

        initialize_db()
        self.client = client
        self.model = model
        self.search_history = []
        
        # Set up logging
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_filename = os.path.join(log_dir, f'lenze_{current_time}.log')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_filename)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.info('**Lenze setup completed, ready to run**s')
    
    def __get_response(self, messages: dict, max_token: int = 600):
        start_time = time.time()
        response = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        max_tokens=max_token
    )
        end_time = time.time()
        self.logger.info(f'API call took {end_time - start_time:.4f} seconds')
        return response.choices[0].message.content

    def analyze(self):
        
        current_date = date.today()
        values = {'query': self.query, 'current_date': current_date}
        prompt = complete_prompt(ANALYZE_PROMPT, values)

        self.logger.info('Starting analysis for query: <%s>', self.query)
        sub_queries = self.__get_response(prompt)
        self.logger.info('Completed analysis for query: <%s>', self.query)

        self.sub_queries = ast.literal_eval(sub_queries)
  
    def search(self):

        urls = []
        sources = []

        start_time = time.time()
        self.logger.info('Start searching for each sub-query')
        
        for sub_query in self.sub_queries:
            values = {'sub_query': sub_query}
            prompt = complete_prompt(OPT_PROMPT, values)
            opt_query = self.__get_response(prompt)
            self.logger.info(f'Optimized query for sub-query <{sub_query}> generated: <{opt_query}>')            
            # new_urls = get_urls(google_api_search(opt_query))
            new_urls = get_urls(google_scrape_search(opt_query))
            urls.extend(new_urls)

        urls = list(set(urls))
        scraped_texts = scrape_urls(urls)
        for url, text in zip(urls, scraped_texts):
            sources.append({'link': url, 'text': text})

        local_store(sources)

        end_time = time.time()
        self.logger.info(f'Finished searching for each sub-query and sources have been stored locally. Actions took {end_time-start_time:.4f} seconds')

    def answer(self):
        start_time = time.time()
        self.logger.info('Start analyzing sources and generating response')

        query_embedding = generate_embedding(self.query)
        sources = local_read()
        most_relevant_sources = find_most_relevant_sources(np.frombuffer(query_embedding, dtype=np.float32), sources)
        values = {'sources': most_relevant_sources, 'query': self.query}
        prompt = complete_prompt(ANSWER_PROMPT, values)
        response = self.__get_response(prompt)
        self.response = response

        output = f'\n=========Answer==========\n{response}'
        self.logger.info(output)
        print(output)

        end_time = time.time()
        self.logger.info(f'Response generated successfully in {end_time-start_time:.4f} seconds')

    def interact(self):
        start_time = time.time()
        self.logger.info('Start generating related queries')
        values = {'query': self.query, 'response': self.response}
        prompt = complete_prompt(INTERACTION_PROPMT, values)
        related_queries = self.__get_response(prompt)
        output = f'\n==========Related==========\n{related_queries}'
        self.logger.info(output)
        print(output)

        end_time = time.time()
        self.logger.info(f'Related queries generated in {end_time-start_time:.4f} seconds')

    def run(self):
        while True:
            try:
                self.query = input("Enter a new query (or press Ctrl+C to exit): ")
                start_time = time.time()
                self.analyze()
                self.search()
                self.answer()
                self.interact()
                end_time = time.time()
                time_taken = f'**Response generated in {end_time-start_time:.4f} seconds**'
                self.logger.info(time_taken)
                print(time_taken)
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt received. Exiting the program.")
                break

