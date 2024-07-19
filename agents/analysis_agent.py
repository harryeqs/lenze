__all__ = ["AnalysisAgent"]

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent
from datetime import date
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
                            "query": {"type": "string", "description": "The original query."},
                            "current_date": {"type": "string", "description": "The current date."}
                        },
                        "required": ["query", "current_date"],
                    },
                }
            }
        )
        self.input_type = "str"
        self.output_type = "str"

        self.llm_analysis = LLMAgent(template=analysis_prompt, llm_client=llm_client, stream=False)

    def flowing(self, query: str, current_date = None):
        current_date = date.today()
        yield f'The current date is: {current_date}.\n'
        yield 'Generating sub-queries...\n'
        yield json.dumps(self.llm_analysis(query=query, current_date=current_date))
        

analysis_prompt = [
    {
        "role": "system",
        "content": """

Instructions for Analyzing and Breaking Down User Queries:

1. **Context Understanding:**
    - Comprehend the user's query to grasp the main topic and intent.
    - Note the current date for any time-sensitive information.
    - **Important:** Do not reference date when asking for prices, unless specified. Do not use word 'current' as well.

2. **Identify Key Elements:**
    - Break down the query to identify:
        - Main subject or topic
        - Specific details or requirements
        - Temporal context, only when relevant (e.g., seasons, trends, upcoming events, latest news, weather).
        
3. **Decompose into Sub-Queries When Necessary:**
    - Generate sub-queries only if the original query needs separation into distinct aspects or comparisons.
    - Ensure sub-queries do not overlap significantly in scope.
    - Merge similar sub-queries into one comprehensive sub-query.
    - Align sub-queries directly with the original query's context and requirements.
    - Use as few sub-queries as possible. Limit to no more than three sub-queries.
    - Do not include command words like 'compare' or 'list' in the sub-queries.

4. **Avoid Redundancy:**
    - Ensure each sub-query addresses a distinct aspect of the main query. However, the sub-query should not be too specific unless specified.
    - If the original query is straightforward, do not generate sub-queries.

5. **Structured Output:**
    - Provide a list of sub-queries (even if only one), ensuring they adhere to the original query's context and requirements.
"""
    },
    {
        "role": "user",
        "content": """
Now, apply these steps and analyze the query:

**Original query:**
{query}

**The current date:**
{current_date}

The output should be a list of sub-queries only.
Do not use the date unless absolutely necessary because it will constrain the search results.
"""
    }
]