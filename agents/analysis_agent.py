__all__ = ["AnalysisAgent"]

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent
import json


class AnalysisAgent(Agent):

    def __init__(self, llm_client: OpenAIClient):
        super().__init__()

        self.set_information(
            {
                "type": "function",
                "function": {
                    "name": "AnalysisAgent",
                    "description": "This function can analyze the query from the user and break it down into sub-queries to be searched by the SearchAgent.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The original query."}
                        },
                        "required": ["query"],
                    },
                }
            }
        )
        self.input_type = "str"
        self.output_type = "str"

        self.llm_analysis = LLMAgent(template=analysis_prompt, llm_client=llm_client, stream=False)

    def flowing(self, query: str):
        yield 'Generating sub-queries...'
        yield json.dumps(self.llm_analysis(query=query))
        

analysis_prompt = [
    {
        "role": "system",
        "content": """
You are an analysis agent. Your task is to analyze the user's query, understand its context and requirements, and decompose it into logical sub-queries if necessary to provide a comprehensive response.

Instructions:
1. **Context Understanding:** Read and understand the user's query to grasp the main topic and intent.

2. **Identify Key Elements:** Break down the query to identify key components, such as:
   - Main subject or topic
   - Specific details or requirements
   - Any implied sub-questions or additional information needed

3. **Decompose into Sub-Queries:**
   - If the query is complex, divide it into smaller, manageable sub-queries.
   - Do not generate any irrelevant sub-queries. For example, there is no need to understand what an event is if I only want the time when it takes place.
   - Searches are expensive so please genereate as few sub-queries as possible.
   - Each sub-query should focus on a specific aspect of the main query to facilitate detailed analysis.
   - **Important:** If the original query is simple enough for searching directly, DO NOT generate any sub-queries.

4. **Structured Output:** Provide a structured analysis that includes:
   - A list of sub-queries only.

"""
    },
    {
        "role": "user",
        "content": """
Now, apply these steps and analyze the query:

**Original query:**
{query}

The output should be a list of sub-queries only.
"""
    }
]