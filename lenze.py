from openai import OpenAI
from tools.google_search import google_api_search, google_scrape_search, get_urls
from tools.source_store import local_store, local_read, initialize_db, generate_embedding, find_most_relevant_sources
from tools.web_scraper import scrape_urls
from datetime import date, datetime
from prompts import CHECK_SEARCH_PROMPT, ANALYZE_PROMPT, ANSWER_PROMPT, INTERACTION_PROPMT
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

def str_to_bool(s):
    if s.lower() in ['true', '1', 't', 'y', 'yes']:
        return True
    elif s.lower() in ['false', '0', 'f', 'n', 'no']:
        return False
    else:
        raise ValueError(f"Cannot convert {s} to boolean.")

class Lenze:
    def __init__(self, client: OpenAI, model: str):

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
        self.logger.info('**Lenze setup completed, ready to run**')
    
    def __get_response(self, messages: dict, max_token: int = 1000):
        start_time = time.time()
        response = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        max_tokens=max_token
    )
        end_time = time.time()
        self.logger.info(f'API call took {end_time - start_time:.4f} seconds')
        return response.choices[0].message.content
    
    def need_search(self):

        values = {'search_history': self.search_history, 'query': self.query}
        prompt = complete_prompt(CHECK_SEARCH_PROMPT, values)
        response = self.__get_response(prompt)
        need_search = str_to_bool(response.strip())  # Convert the string response to a boolean
        self.logger.info(f"Additional sources needed for query <{self.query}>: <{need_search}>")
        return need_search

    def analyze(self):
        
        current_date = date.today()
        values = {'query': self.query, 'current_date': current_date, 'search_history': self.search_history}
        prompt = complete_prompt(ANALYZE_PROMPT, values)
        sub_queries = self.__get_response(prompt)
        self.sub_queries = ast.literal_eval(sub_queries)
        self.logger.info(f"Sub-queries for query <{self.query}> generated: <{self.sub_queries}>")
  
    def search(self):

        urls = []
        sources = []

        start_time = time.time()
        self.logger.info('Start searching for each sub-query')
        
        for sub_query in self.sub_queries:
            values = {'sub_query': sub_query}  
            # new_urls = get_urls(google_api_search(opt_query))
            new_urls = get_urls(google_scrape_search(sub_query))
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
        self.logger.info(f'Answer generated successfully in {end_time-start_time:.4f} seconds')

        self.search_history.append({'query:': self.query, 'response': self.response})

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

        print("======Welcome! I'm Lenze and I will help with your queries======")
        global_start = time.time()

        while True:
            try:
                self.query = input("Enter a new query (or press Ctrl+C to exit): ")
                self.logger.info(f'New query received: <{self.query}>')
                print(f'\n=====Query=====\n{self.query}')
                start_time = time.time()
                
                if self.need_search():
                    self.analyze()
                    self.search()

                self.answer()
                self.interact()
                end_time = time.time()
                time_taken = f'**Response generated in {end_time-start_time:.4f} seconds**'
                self.logger.info(time_taken)
                print(f'\n{time_taken}\n')
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt received. Exiting Lenze.")
                break
            except Exception as e:
                error = f'An error occurred: {str(e)}' 
                self.logger.error(error)
                print(error)
                break
        
        global_end = time.time()
        self.logger.info(f'**Lenze ran for {global_end-global_start:.4f} seconds, exiting.**')
            
