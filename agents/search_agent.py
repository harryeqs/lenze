__all__ = ["SearchAgent"]

from typing import Any

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent
from tools.google_search import google_search

class SearchAgent(Agent):

    def __init__(self, llm_client: OpenAIClient):
        super().__init__()

        self.set_information(
            {
                "type": "function",
                "function": {
                    "name": "SearchAgent",
                    "description": "This function can search across the internet on a topic provided by the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "The question here which need help."}
                        },
                        "required": ["question"],
                    },
                }
            }
        )
        self.input_type = "str"
        self.output_type = "list"

        self.llm_search = LLMAgent(template=search_prompt, llm_client=llm_client, stream=True)

    def flowing(self, question: str) -> Any:
        return self.llm_search(question=question, tools=[google_search])
    


search_prompt = [
    {
        "role": "system",
        "content": """
You are a search assistant who can help user to search across the internet about a specific topic.
Ignore any sources that appear to be advertisements.
Use the tool google_search. Whenever you use it, notify the user by outputting "Searching via Google".
"""},
    {
        "role": "user",
        "content": """
The question:
{question}

Please give me the urls to the first 10 relevant search results.
"""}]