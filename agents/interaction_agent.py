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
                    "description": "This function can suggest related questions based on recent responses.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "The question here which need help."},
                            "response": {"type": "string", "description": "Latest response."}
                        },
                        "required": ["question", "response"],
                    },
                }
            }
        )
        self.input_type = "str"
        self.output_type = "str"

        self.llm_search = LLMAgent(template=summary_prompt, llm_client=llm_client, stream=True)

    def flowing(self, question: str, response: str) -> Any:
        return self.llm_search(question=question, response=response)
    


summary_prompt = [
    {
        "role": "system",
        "content": """
You are an assistant to suggest three related questions based on the latest pair of question and response.
Do not simply repeat or paraphrase the last question.
Please use the response to get inspirations on related questions.
"""},
    {
        "role": "user",
        "content": """
Last question:
{question}
Last response:
{response}

Please give me three related questions based on the last pair of question and response.
"""}]