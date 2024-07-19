from openai import OpenAI
from tools.google_search import google, get_urls
from tools.source_store import local_store, local_read, initialize_db
from tools.web_scraper import scrape_urls
from datetime import date
from prompts import ANALYZE_PROMPT, OPT_PROMPT, ANSWER_PROMPT, INTERACTION_PROPMT
import json

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
            filled_content = filled_content.replace(f'{{{placeholder}}}', value)
        filled_template.append({"role": part["role"], "content": filled_content})

    return filled_template

class Lenze:
    def __init__(self, client: OpenAI, model: str, mode: str="default"):
        initialize_db()
        self.client = client
        self.model = model
    
    def __get_response(self, messages: dict):
        response = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        max_tokens=1000,
    )
        return response.choices[0].message.content

    def analyze(self, query: str):
        pass

    def search(self, sub_queries: list):
        pass

    def answer(self, query: str):
        pass

    def interact(self, query: str, response: str):
        pass

    def run(self, query: str):
        pass