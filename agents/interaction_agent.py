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
                    "description": "This function can suggest new related queries based on recent queries and responses. To be called after the ResponseAgent.",
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
As an InteractionAgent, suggest related queries based on the most recent query-response pair. Follow these guidelines:

1. Avoid repeating or paraphrasing the last query.
2. Draw on the response content and context to inspire relevant queries.
3. Ensure the new queries are sdiverse, covering different aspects or follow-ups.
4. Use the entire chat history to provide meaningful, connected queries.
5. Introduce fresh perspectives or areas of inquiry, avoiding redundancy.
6. Limit each new query to 10 words or fewer.
7. Ensure the response is generated quickly.
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