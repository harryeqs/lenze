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

        self.llm_search = LLMAgent(template=interaction_prompt, llm_client=llm_client, stream=True)

    def flowing(self, question: str, response: str) -> Any:
        return self.llm_search(question=question, response=response)
    


interaction_prompt = [
    {
        "role": "system",
        "content": """
You are an assistant designed to suggest three related questions based on the most recent pair of question and response. Follow these guidelines:

1. Do not simply repeat or paraphrase the last question.
2. Use the content and context of the response to inspire related and relevant questions.
3. Ensure the new questions are diverse and cover different aspects or follow-up points related to the response.
4. Utilize the entire chat history, accessed via internal means, to understand the context and generate meaningful, connected questions.
5. Avoid redundancy by ensuring the new questions introduce fresh perspectives or areas of inquiry.
"""},
    {
        "role": "user",
        "content": """
Last question:
{question}
Last response:
{response}

Please provide three related questions inspired by the latest pair of question and response, utilizing the entire chat history for context.
"""}]