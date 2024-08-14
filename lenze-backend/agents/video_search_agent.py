from tools.google_search import SearchEngine
from .base.base_agent import BaseAgent
from .base.prompts import complete_template, VIDEO_SEARCH_PROMPT
from openai import OpenAI

__all__ = ["VideoSearchAgent"]

class VideoSearchAgent(BaseAgent):

    def search(self):
        
        values = {'query': self.query, 'search_history': self.search_history}
        self.search_history.append(self.query)
        message = complete_template(VIDEO_SEARCH_PROMPT, values)
        refined_query = self._get_response(message)
        video_ids = self.search_engine.video_search(refined_query)
        
        return video_ids



