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
                    "description": "This function can analyse and produce a concise response to an original query based on sources provided and suggest related queries. To be called ONLY ONCE.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The ORIGINAL query input by the user at the start."},
                        },
                        "required": ["query"],
                    },
                }
            }
        )
        self.input_type = "str"
        self.output_type = "str"

        self.llm_answer = LLMAgent(template=answer_prompt, llm_client=llm_client, stream=False)
        self.llm_interaction = LLMAgent(template=interaction_prompt, llm_client=llm_client, stream=False)

    def flowing(self, query: str):

        query_embedding = generate_embedding(query)
        sources = local_read()
        most_relevant_sources = find_most_relevant_sources(np.frombuffer(query_embedding, dtype=np.float32), sources)

        yield '\n========**Answer**========\n'
        response = self.llm_answer(query=query, sources=most_relevant_sources)
        yield response

        yield '\n\n=====**Related**=====\n'
        yield self.llm_interaction(query=query, response=response)

        

answer_prompt = [
    {
        "role": "system",
        "content": """
**Note to AI Manager:**
    - Use the **original query** provided by the user at the start.
    - Run the ResponseAgent only once. Always check if you have already called the ResponseAgent.
    - Remember to mark the ResponseAgent's work as completed.

**Instructions for Responding to the Original Query:**

1. **Understand the Query:**
    - Read the user's original query carefully.
    - Identify the core question and key details.

2. **Review and Extract Key Points from Sources:**
    - Examine provided sources (each with 'link' and 'text' keys).
    - Extract only information directly answering the user's query. Do not include additional details.
    - Try to use various sources for comprehensive information.
    - Ignore extraneous or unrelated content.

3. **Organize Extracted Information:**
    - Group related information logically.
    - Ensure a clear and comprehensive flow.

4. **Compose a Focused Answer:**
    - Write a concise, clear response.
    - Integrate extracted information seamlessly.
    - Provide accurate, short points instead of lengthy explanations.
    - Do not provide additional details that are not asked explicitly in the original query.

5. **Cite Sources Appropriately:**
    - Cite each piece of information strictly in the format (source: website-name [url]).
    - Example: (source: Apple [https://developer.apple.com/news/])
    - Do not include any other information in the citatsion.

6. **Format the Final Answer:**
    - Ensure readability using bullet points or headings.
    - Keep the response directly related to the query without unnecessary details.
    - Make the response short, concise, and focused on the core information needed.

**Emphasis:**
    - Focus on essential information required to answer the query.
    - Avoid irrelevant or redundant information.
    - If an answer cannot be provided, inform the user concisely.
""" },
    {
        "role": "user",
        "content": """
Based on the following sources, please respond to the original query comprehensively and cite each source for the information provided.
Remember to use the **original query** not the sub-queries.
**Original Query:** {query}

**Sources:**
{sources}

The final output should address the query and provide citations for each piece of information strictly in the required format. Please do not include the steps.
Ensure that the link to the source is included in the citation.

DO NOT REPEATEDLY CALL THIS AGENT.
"""
    }
]

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
6. Limit each new query to 15 words or fewer.
7. Ensure the response is generated quickly.
""" },
    {
        "role": "user",
        "content": """
Last query:
{query}
Last response:
{response}

Please provide 5 related queries inspired by the latest pair of query and response, utilizing the entire chat history for context.
Each query should be less than 15 words.
"""}]