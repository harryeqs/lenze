from tools.google_search import SearchEngine
from .base.base_agent import BaseAgent
from .base.prompts import complete_template, IMAGE_SEARCH_PROMPT
from openai import OpenAI

__all__ = ["ImageSearchAgent"]

class ImageSearchAgent(BaseAgent):

    def search(self):
        
        values = {'query': self.query, 'search_history': self.search_history}
        self.search_history.append(self.query)
        message = complete_template(IMAGE_SEARCH_PROMPT, values)
        refined_query = self._get_response(message)
        image_urls = self.search_engine.image_search(refined_query)
        
        return image_urls