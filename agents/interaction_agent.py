__all__ = ["InteractionAgent"]

from typing import Any

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent

class InteractionAgent(Agent):

    def __init__(self, llm_client: OpenAIClient):
        super().__init__()

        self.set_information(
            {
                "type": "function",
                "function": {
                    "name": "InteractionAgent",
                    "description": "This function can suggest new related queries based on recent queries and responses.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The original query."},
                            "response": {"type": "string", "description": "Latest response."}
                        },
                        "required": ["query", "response"],
                    },
                }
            }
        )
        self.input_type = "str"
        self.output_type = "str"

        self.llm_interaction = LLMAgent(template=interaction_prompt, llm_client=llm_client, stream=True)

    def flowing(self, query: str, response: str) -> Any:
        return self.llm_interaction(query=query, response=response)
        

interaction_prompt = [
    {
        "role": "system",
        "content": """
You are an assistant designed to suggest three related queries based on the most recent pair of query and response. Follow these guidelines:

1. Do not simply repeat or paraphrase the last query.
2. Use the content and context of the response to inspire related and relevant queries.
3. Ensure the new queries are diverse and cover different aspects or follow-up points related to the response.
4. Utilize the entire chat history, accessed via internal means, to understand the context and generate meaningful, connected queries.
5. Avoid redundancy by ensuring the new queries introduce fresh perspectives or areas of inquiry.
6. Keep the queries moderately short.
"""},
    {
        "role": "user",
        "content": """
Last query:
{query}
Last response:
{response}

Please provide 5 related queries inspired by the latest pair of query and response, utilizing the entire chat history for context.
"""}]