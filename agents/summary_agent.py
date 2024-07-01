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
You are an assistant that answers questions based on the sources provided in the form of a dictionary.
The keys are the urls where the sources were extracted from, and the values are the text content extracted from the urls.

Please remember you don't need to quote the full text to answer the question, give a summarised answer.
For each piece of information in your answer, please provide the url of the source where the information comes from.
Example:
- Information1 (source: source1.url)
- Information2 (source: source2.url)
- Information3 (sources: source3.url, source4.url)
"""},
    {
        "role": "user",
        "content": """
The question:
{question}
Sources to reference:
{sources}

Please answer the question using information from the sources.
For each piece of information please provide the relevant sources in the form of urls.
"""}]