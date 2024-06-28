__all__ = ["SearchAgent"]

from typing import Any

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent

class SearchAgent(Agent):

    def __init__(self, llm_client: OpenAIClient):
        super().__init__()

        self.set_information(
            {
                "type": "function",
                "function": {
                    "name": "SearchAgent",
                    "description": "This function can search over the internet on a topic specified by the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "The question here which need help.",
                            }
                        },
                        "required": ["question"],
                    },
                }
            }
        )
        self.input_type = "str"
        self.output_type = "str"

        self.llm_plan = LLMAgent(template=search_prompt, llm_client=llm_client, stream=True)

    def flowing(self, question: str) -> Any:
        return self.llm_plan(question=question)
    


search_prompt = """
"""