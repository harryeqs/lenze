__all__ = ["SummaryAgent"]

from typing import Any

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent

class SummaryAgent(Agent):

    def __init__(self, llm_client: OpenAIClient):
        super().__init__()

        self.set_information(
            {
                "type": "function",
                "function": {
                    "name": "SummaryAgent",
                    "description": "This function can search across the internet on a topic provided by the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "The question here which need help."},
                            "sources": {"type": "string", "description": "Sources to retrieve information from."}
                        },
                        "required": ["question", "sources"],
                    },
                }
            }
        )
        self.input_type = "dict"
        self.output_type = "str"

        self.llm_search = LLMAgent(template=summary_prompt, llm_client=llm_client, stream=True)

    def flowing(self, question: str, sources: dict) -> Any:
        return self.llm_search(question=question, sources = sources)
    


summary_prompt = [
    {
        "role": "system",
        "content": """
You are an assistant that answers questions based on the sources provided in the form of a dictionary. The dictionary keys are URLs from which the sources were extracted, and the values are the text content extracted from these URLs.

Guidelines:
1. Provide a concise, summarized answer to the question.
2. Do not quote the full text; instead, extract and summarize the key information.
3. For each piece of information in your answer, include the URL of the source where the information originates.
4. Ensure clarity and accuracy in your references to the sources.

Example format:
- Information1 (source: http://example.com/source1)
- Information2 (source: http://example.com/source2)
- Information3 (sources: http://example.com/source3, http://example.com/source4)
"""},
    {
        "role": "user",
        "content": """
The question:
{question}
Sources to reference:
{sources}

Please answer the question using information from the provided sources. For each piece of information, include the relevant source URLs.
"""}]