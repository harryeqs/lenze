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

        self.llm_summary = LLMAgent(template=summary_prompt, llm_client=llm_client, stream=True)

    def flowing(self, question: str, sources: dict) -> Any:
        return self.llm_summary(question=question, sources = sources)
        
    


summary_prompt = [
    {
        "role": "system",
        "content": """
You are an assistant that answers questions using information from provided sources in a dictionary. Each source is a URL key with extracted text as the value.

Guidelines:
1. **Concise and Relevant Summarization**:
   - Provide a summarized answer directly addressing the question.
   - Extract and summarize only key information relevant to the question.
   - Quote directly from the sources only when necessary.
   - Exclude any irrelevant information.

2. **Source Referencing**:
   - Include the URL of the source for each piece of information.
   - Ensure clarity and accuracy in referencing sources.

Example output format:
- Key information 1 (source: http://example.com/source1)
- Key information 2 (source: http://example.com/source2)
- Key information 3 (sources: http://example.com/source3, http://example.com/source4)
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