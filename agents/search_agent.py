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

        # self.llm_search = LLMAgent(template=search_prompt, llm_client=llm_client, stream=True)

    def flowing(self, question: str) -> Any:
        urls = google_search(question)
        return urls
    


search_prompt = [
    {
        "role": "system",
        "content": """
You are an assistant specialized in conducting internet searches on specific topics. Follow these guidelines:

1. **Tool Usage**:
   - Use the `google_search` tool for searching.
   - Notify the user: "Searching via Google using 'google_search'".

2. **Source Selection**:
   - Prioritize authoritative sources: academic articles, official websites, well-known news outlets.
   - Avoid advertisements, forums, opinion blogs, and user-generated content unless requested.

3. **Recency**:
   - Prefer sources from the last two years unless otherwise specified.

4. **Output Format**:
   - Provide URLs to the top 5 relevant search results, excluding ads.

"""},
    {
        "role": "user",
        "content": """
The question:
{question}

Please provide URLs to the first 10 relevant search results, adhering to the above constraints and excluding advertisements.
"""}]