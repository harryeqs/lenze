from openai import OpenAI

__all__ = ["BaseAgent"]

class BaseAgent:
    def __init__(self, client: OpenAI, model: str):

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
    
    async def _get_response_stream(self, messages: dict, max_token: int = 1000):
        response_stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_token,
            stream=True
        )

        for event in response_stream:
            if "content" in event.choices[0].delta:
                current_response = event.choices[0].delta.content
                print(current_response)
                yield current_response