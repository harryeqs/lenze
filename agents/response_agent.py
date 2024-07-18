__all__ = ["ResponseAgent"]

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent
from tools.source_store import local_read, generate_embedding, find_most_relevant_sources
import numpy as np

class ResponseAgent(Agent):

    def __init__(self, llm_client: OpenAIClient):
        super().__init__()

        self.set_information(
            {
                "type": "function",
                "function": {
                    "name": "ResponseAgent",
                    "description": "This function can analyse and produce a concise response to an original query based on sources provided. To be called ONLY ONCE.",
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

        query_embedding = generate_embedding(query)
        sources = local_read()
        most_relevant_sources = find_most_relevant_sources(np.frombuffer(query_embedding, dtype=np.float32), sources)
        
        return self.llm_response(query=query, sources=most_relevant_sources)

        

response_prompt = [
    {
        "role": "system",
        "content": """

**Note to AI Manager:**
    - Run the ResponseAgent only once. Always check if you have already called the ResponseAgent.
    - Remember to mark the ResponseAgent's work as completed.
    - After the Response Agent completes, run the InteractionAgent.

As a response agent, your task is to respond to the original query based the provided sources. Follow these steps to ensure a concises and accurate response.

Instructions for Responding to the Original Query:

1. **Understand the Query:**
    - Read the user's original query carefully.
    - Identify the core question and key details.

2. **Review and Extract Key Points from Sources:**
    - Examine provided sources (each with 'link' and 'text' keys).
    - Extract information directly answering the user's query.
    - Ignore extraneous or unrelated content.

3. **Organize Extracted Information:**
    - Group related information.
    - Ensure logical flow and comprehensive coverage of the query.

4. **Compose a Focused Answer:**
    - Write a concise and clear response.
    - Integrate extracted information smoothly.
    - Provide short, accurate points instead of a long report.

5. **Cite Sources Appropriately:**
    - Cite each piece of information strictly in the format (source: [website-name]<url>).
    - Do not include any other information in the citation.

6. **Format the Final Answer:**
    - Ensure readability with bullet points or headings if necessary.
    - Keep the response directly related to the query without unnecessary details.

**Emphasis:**
    - Focus on core information needed to answer the query.
    - Avoid irrelevant or redundant information.
    - If an answer cannot be provided, inform the user.

""" },
    {
        "role": "user",
        "content": """
Based on the following sources, respond to the original query comprehensively and cite each source for the information provided.
Remember to use the original query not the sub-queries.
**Original Query:** {query}

**Sources:**
{sources}

The final output should address the query and provide citations for each piece of information strictly in the required format. Please do not include the steps.
Ensure that the link to the source is included in the citation.

DO NOT REPEATEDLY CALL THIS AGENT.
"""
    }
]