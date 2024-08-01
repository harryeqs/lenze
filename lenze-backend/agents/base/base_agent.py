from openai import OpenAI

__all__ = ["BaseAgent"]

class BaseAgent:
    def __init__(self, client: OpenAI, model: str):

        self.client = client
        self.model = model
        self.search_history = []
    
    def _get_response(self, messages: dict, max_token: int = 1000, stream=True):
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
            
        return full_response