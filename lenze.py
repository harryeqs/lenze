from openai import OpenAI
from tools.google_search import google, get_urls
from tools.source_store import local_store, local_read, initialize_db
from tools.web_scraper import scrape_urls
from datetime import date, datetime
from prompts import ANALYZE_PROMPT, OPT_PROMPT, ANSWER_PROMPT, INTERACTION_PROPMT
import os
import time
import json
import logging

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
        self.logger.info('Lenze set up complete, ready to run')
    
    def __get_response(self, messages: dict, max_token: int = 100):
        start_time = time.time()
        response = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        max_tokens=max_token
    )
        end_time = time.time()
        self.logger.info(f"API call took {end_time - start_time} seconds")
        return response.choices[0].message.content

    def analyze(self, query: str):

        current_date = date.today()
        values = {'query': query, 'current_date': current_date}
        prompt = complete_prompt(ANALYZE_PROMPT, values)

        self.logger.info('Starting analysis for query: %s', query)
        sub_queries = self.__get_response(prompt)
        self.logger.info('Completed analysis for query: %s', query)

        return sub_queries
  
    def search(self, sub_queries: list):
        pass

    def answer(self, query: str):
        pass

    def interact(self, query: str, response: str):
        pass

    def run(self, query: str):
        pass