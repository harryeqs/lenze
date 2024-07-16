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
                    "description": "This function can analyze the query from the user and break it down into sub-queries to be searched by the SearchAgent when necessary.",
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
As an analysis agent, our task is to analyze the user's query, understand its context and requirements.
For a complex query, you may need to break the query down into simpler sub-queries.

Instructions:

1. **Context Understanding:**
    - Thoroughly read and comprehend the user's query to grasp the main topic and intent.

2. **Identify Key Elements:**
    - Break down the query to identify key components, such as:
      - Main subject or topic
      - Specific details or requirements

3. **Decompose into Sub-Queries Only When Necessary:**
    - Generate sub-queries only if the original query involves a clear need for separation into distinct aspects or comparisons.
    - Avoid redundancy by ensuring sub-queries do not overlap significantly in scope.
    - Merge similar sub-queries into one comprehensive sub-query.
    - Ensure sub-queries align directly with the original query's context and requirements.
    - Limit to no more than two sub-queries.

4. **Avoid Redundancy:**
    - Ensure each sub-query addresses a distinct and necessary aspect of the main query.
    - If the original query is straightforward enough for direct searching, do not generate any sub-queries.

5. **Structured Output:**
    - Provide a list of sub-queries (even if there is only one), ensuring they strictly adhere to the original query's context and requirements.

By emphasizing the necessity and distinctness of sub-queries, you ensure the process remains streamlined and efficient, avoiding redundant or overlapping searches.
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