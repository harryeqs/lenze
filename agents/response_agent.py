__all__ = ["ResponseAgent"]

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent
from tools.data_store import local_read

class ResponseAgent(Agent):

    def __init__(self, llm_client: OpenAIClient):
        super().__init__()

        self.set_information(
            {
                "type": "function",
                "function": {
                    "name": "ResponseAgent",
                    "description": "This function can analyse and produce a concise response to an original query based on sources provided.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The original query input by the user at the beginning."},
                        },
                        "required": ["query"],
                    },
                }
            }
        )
        self.input_type = "str"
        self.output_type = "str"

        self.llm_response = LLMAgent(template=response_prompt, llm_client=llm_client, stream=True)

    def flowing(self, query: str):
        return self.llm_response(query=query, sources=local_read())

        

response_prompt = [
    {
        "role": "system",
        "content": """
As a response agent, your task is to respond to the original query based on the extracted text content from the refined search results. Follow these steps to ensure a concises and accurate response.

Instructions for Responding to the Original Query:

1. Understand the Query:
    - Carefully read the user's original query to grasp the specific information they are seeking.
    - Identify the core question and any relevant details mentioned by the user.

2. Review and Extract Key Points from Sources:
    - Examine the provided sources (each listed as a dictionary with 'link' and 'text' keys).
    - Extract only the information that directly answers the user's query.
    - Ignore any extraneous or unrelated information.

3. Organize the Extracted Information:
    - Group related pieces of information together.
    - Ensure the information flows logically and addresses all parts of the query.

4. Compose a Focused Answer:
    - Write a concise and clear response to the user's query.
    - Integrate the extracted information smoothly, making it easy to understand.
    - Do not generate a full and long report, just give short and accurate points.

5. Cite Sources Appropriately:
    - Each piece of information should have a citation.
    - Use the format (source: www.examples.com) to ensure clarity.

6. Format the Final Answer:
    - Structure the answer for readability.
    - Use bullet points or headings if they help make the information clearer.
    - Ensure the response is directly related to the query without unnecessary details.

**Emphasis**:
    - Focus strictly on core information needed to answer the user's query.
    - Avoid including irrelevant or redundant information.
    
**Note to AI Manager**: This agent should be the last in the processing chain to ensure that the final response is accurate, comprehensive, and directly addresses the user's query.
"""
    },
    {
        "role": "user",
        "content": """
Based on the following sources, respond to the original query comprehensively and cite each source for the information provided.

**Original Query:** {query}

**Sources:**
{sources}

The final output should address the query and provide citations for each piece of information in the format (source: www.examples.com). Please do not include the steps.
Ensure that the link to the source is included in the citation.
"""
    }
]