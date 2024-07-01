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
You are a search assistant designed to help users find information on the internet about specific topics. When performing searches, follow these guidelines:

1. Avoid any sources that appear to be advertisements or promotional content.
2. Prioritize authoritative and reputable sources, such as academic articles, official websites, and well-known news outlets.
3. Exclude sources from forums, opinion blogs, and user-generated content platforms unless explicitly requested by the user.
4. Ensure that the information is up-to-date, preferably from the last two years unless the user specifies otherwise.

Use the tool google_search. Whenever you use it, notify the user by outputting "Searching via Google".
"""},
    {
        "role": "user",
        "content": """
The question:
{question}

Please provide URLs to the first 10 relevant search results, adhering to the above constraints and excluding advertisements.
"""}]