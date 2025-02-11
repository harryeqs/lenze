from openai import OpenAI
from tools.google_search import SearchEngine
import asyncio

__all__ = ["BaseAgent"]

class BaseAgent:
    def __init__(self, client: OpenAI, model: str, session_id: int, search_engine: SearchEngine):
        self.session_id = session_id
        self.search_engine = search_engine
        self.client = client
        self.model = model
        self.search_history = []
    
    def _get_response(self, messages: dict, max_token: int = 1000):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_token,
            stream=False
        )

        return response.choices[0].message.content
    
    def _get_response_stream(self, messages: dict, max_token: int = 1000):
        response_stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_token,
            stream=True
        )

        for chunk in response_stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content

    async def _async_generator_wrapper(self, generator):
        loop = asyncio.get_event_loop()
        for item in generator:
            yield await loop.run_in_executor(None, lambda: item)

    def _format_event(self, content):
        return f"data: {content}\n\n"
