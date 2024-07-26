from openai import OpenAI
from tools.google_search import google_api_search, google_scrape_search, get_urls
from tools.source_store import local_store, local_read, initialize_db, generate_embedding, find_most_relevant_sources
from tools.text_extraction import process_urls
from datetime import date, datetime
from prompts import ANALYZE_PROMPT, ANSWER_PROMPT, INTERACTION_PROPMT
import numpy as np
import os
import time
import logging
import json

__all__ = ["Lenze"]

def complete_template(template, values):
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
    
    def __get_response(self, messages: dict, max_token: int = 1000, stream=True):
        start_time = time.time()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_token,
            stream=stream
        )
        
        if stream:
            full_response = ""
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content is not None:
                    full_response += content
                    print(content, end='', flush=True)
        else:
            full_response = response.choices[0].message.content
            
        end_time = time.time()
        self.logger.info(f'API call took {end_time - start_time:.4f} seconds')
        
        return full_response
            

    def analyze(self):
        
        self.logger.info("Analysis start")
        current_date = date.today()
        values = {'query': self.query, 'current_date': current_date, 'search_history': self.search_history}
        message = complete_template(ANALYZE_PROMPT, values)
        analysis = self.__get_response(message, stream=False)
        analysis = json.loads(analysis)
        need_search, refined_query = analysis["need_search"], analysis["refined_query"]
        self.logger.info(f"Analysis completed, need for search: <{need_search}>, refined query: <{refined_query}>")
        return need_search, refined_query
  
    def search(self, query):

        urls = []
        sources = []

        start_time = time.time()
        print('\nSearching on web...\n')
        self.logger.info('Start searching for each sub-query')
        
        search_start = time.time()
        urls = get_urls(google_scrape_search(query))
        search_end = time.time()
        self.logger.info(f'Searching took {search_end-search_start:.4f} seconds')

        urls = list(set(urls))

        scrape_start = time.time()
        scraped_texts = process_urls(urls)
        sources = [{'link': url, 'text': text} for url, text in zip(urls, scraped_texts)]
        scrape_end = time.time()
        self.logger.info(f'Scraping took {scrape_end-scrape_start:.4f} seconds')

        store_start = time.time()
        local_store(sources)
        store_end = time.time()
        self.logger.info(f'Storing took {store_end-store_start:.4f} seconds')

        end_time = time.time()
        self.logger.info(f'**Search and source storage took {end_time-start_time:.4f} seconds**')

    def answer(self):

        start_time = time.time()
        self.logger.info('Start analyzing sources and generating response')

        query_embedding = generate_embedding(self.query)
        sources = local_read()
        most_relevant_sources = find_most_relevant_sources(np.frombuffer(query_embedding, dtype=np.float32), sources)
        values = {'sources': most_relevant_sources, 'query': self.query}
        message = complete_template(ANSWER_PROMPT, values)
    
        print('\n=====Answer=====\n')
        response = self.__get_response(message)
        self.response = response

        self.logger.info('\n=====Answer=====\n' + response)

        end_time = time.time()
        self.logger.info(f'Answer generated successfully in {end_time-start_time:.4f} seconds')

        self.search_history.append({'query:': self.query, 'response': self.response})

    def interact(self):

        start_time = time.time()
        self.logger.info('Start generating related queries')
        values = {'query': self.query, 'response': self.response}
        message = complete_template(INTERACTION_PROPMT, values)

        print('\n\n=====Related=====\n')
        related_queries = self.__get_response(message)
        
        self.logger.info('\n=====Related=====\n' + related_queries)

        end_time = time.time()
        self.logger.info(f'\nRelated queries generated in {end_time-start_time:.4f} seconds')

    def run(self):

        print("======Welcome! I'm Lenze and I will help with your queries======")
        global_start = time.time()

        while True:
            try:
                self.query = input("Enter a new query (or press Ctrl+C to exit): ")
                self.logger.info(f'New query received: <{self.query}>')
                start_time = time.time()
                
                need_search, refined_query = self.analyze()
                
                if need_search:
                    self.search(refined_query)
                
                self.answer()
                self.interact()

                end_time = time.time()
                time_taken = f'**Response generated in {end_time-start_time:.4f} seconds**'
                self.logger.info(time_taken)
                print(f'\n{time_taken}\n')
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt received. Exiting Lenze.")
                break
            # except Exception as e:
            #     error = f'An error occurred: {str(e)}' 
            #     self.logger.error(error)
            #     print(error)
            #     break
        
        global_end = time.time()
        self.logger.info(f'**Lenze ran for {global_end-global_start:.4f} seconds, exiting.**')


from dotenv import load_dotenv

if __name__ == '__main__':

    # Load environment variables
    load_dotenv()

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)
    lenze = Lenze(client, model='gpt-3.5-turbo')
    
    lenze.run() 