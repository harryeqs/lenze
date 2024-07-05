__all__ = ["SummaryAgent"]

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
                            "query": {"type": "string", "description": "The original query here which need help."},
                            "sources": {"type": "string", "description": "Sources to retrieve information from."}
                        },
                        "required": ["query", "sources"],
                    },
                }
            }
        )
        self.input_type = "str", "list"
        self.output_type = "str"

        self.llm_summary = LLMAgent(template=summary_prompt, llm_client=llm_client, stream=False)

    def flowing(self, query: str, sources: list ):
        
        response = self.llm_summary(query=query, sources=sources)

        return response
        
    


summary_prompt = [
    {
        "role": "system",
        "content": """
As a summary agent, your task is to respond to the original query based on the extracted text content from the refined search results. Follow these steps to ensure a thorough and accurate response:

1. **Understand the Query**:
   - Carefully analyze the original query to fully understand the user's intent and the specific information they are seeking.

2. **Review Sources**:
   - Thoroughly review the provided sources, each listed as a dictionary with the source index as the key and a dictionary as the content. The content dictionary includes 'link' and 'text' keys.
   - Extract key points, data, and insights that directly address the user's query.

3. **Organize Information**:
   - Organize the extracted information logically and coherently.
   - Ensure that each piece of information is clearly linked to its respective source.

4. **Compose the Answer**:
   - Write a comprehensive answer to the original query.
   - Seamlessly integrate information from the sources, making sure to cite each source appropriately.

5. **Cite Sources**:
   - For each piece of information included in the answer, provide a citation in the format: (source: [link to the source]). Ensure the link to the source is included in the citation.

6. **Format the Answer**:
   - Ensure the final answer is well-structured, clear, and easy to read.
   - Use paragraphs, bullet points, or headings as necessary to enhance readability.
   - Answer strictly on the specific question asked. For example, if the query is about the weather today, provide only today's weather information without discussing other time periods.
"""
    },
    {
        "role": "user",
        "content": """
Based on the following sources, respond to the original query comprehensively and cite each source for the information provided.

**Original Query:** {query}

**Sources:**
{sources}

The final output should address the query and provide citations for each piece of information in the format [source-1: url-1]. Please do not include the steps.
Ensure that the link to the source is included in the citation.
"""
    }
]