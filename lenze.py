from openai import OpenAI
from tools.google_search import google, get_urls
from tools.source_store import local_store, local_read, initialize_db
from tools.web_scraper import scrape_urls
from datetime import date
import json

__all__ = ["Lenze"]

class Lenze:
    def __init__(self, client: OpenAI, model: str, mode: str="default"):
        self.client = client
        self.model = model

    def __analyze(self, query: str):
        pass

    def __search(self, sub_queries: list):
        pass

    def __respond(self, query: str):
        pass

    def __interact(self, query: str, response: str):
        pass

    def run(self, query: str):
        pass