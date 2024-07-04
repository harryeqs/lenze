__all__ = ["SearchAgent"]

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent
from tools.google_search import google_search
from tools.web_scraper import scrape_url
import json

class SearchAgent(Agent):

    def __init__(self, llm_client: OpenAIClient):
        super().__init__()

        self.set_information(
            {
                "type": "function",
                "function": {
                    "name": "SearchAgent",
                    "description": "This agent can search across the internet on a query provided by the user by following the searching process and return a list of raw source data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The query here which need help."}
                        },
                        "required": ["query"],
                    },
                }
            }
        )
        self.input_type = "str"
        self.output_type = "list"

        self.opt_agent = LLMAgent(template=opt_prompt, llm_client=llm_client, stream=False)
        self.refine_agent = LLMAgent(template=refine_prompt, llm_client=llm_client, stream=False)

    def flowing(self, query: str):

        # Generate optimised query
        opt_query = self.opt_agent(query=query)
        print(f'**Optimized query**: \n {opt_query}' +
              f'\n --------------------')

        # Search using optimised query
        results = google_search(opt_query)
        print(f'**Search results**: \n {results}' +
              f'\n --------------------')

        # Refine the search results
        refined_results = self.refine_agent(query=query, results=results)
        print(f'**Refined results**: {refined_results}')
        results =json.loads(refined_results)

        # scrape URLs contained in search results and returned compiled sources
        sources = []
        counter = 1

        for result in results:
            result['text'] = scrape_url(result['link'])
            result.pop('snippet')
            sources.append({f'source-{counter}': result})
            counter += 1

        return sources
    

opt_prompt = [
    {
        "role": "system",
        "content": """
As an intelligent search optimization agent, your task is to refine and optimize a given query to achieve the most accurate and relevant results on Google. Follow these steps to enhance the query:

1. **Understand the Query:** Analyze the initial query to understand the key concepts and the user's intent. Identify the main topic, specific details, and any implicit or explicit requirements. 

2. **Refine Keywords:** Break down the query into essential keywords. Add or modify these keywords to include synonyms, related terms, and variations that capture the full scope of the user's intent. Avoid using excessive quotation marks.

3. **Use Operators:** Utilize Google search operators to narrow down the results when necessary. This includes:
   - Quotation marks ("") sparingly to search for exact phrases only when absolutely necessary.
   - The minus sign (-) to exclude unwanted terms.
   - The site: operator to limit results to a specific website or domain.
   - The filetype: operator to find specific types of files (e.g., PDFs, DOCs).
   - The intitle: operator to ensure the main keyword is in the title of the results.

4. **Incorporate Filters:** Consider adding filters like location, date range, or language to make the search results more relevant. For example, adding "2024" to find the most recent information or specifying "site:.edu" for educational resources.

5. **Special Case Handling:**
   - **Date-Specific Queries:** For queries that involve a specific day of the week (e.g., "events next Monday"), automatically determine the date based on the current date and incorporate it into the search query.

6. **Formulate the Optimized Query:** Combine the refined keywords, operators, and filters into a coherent and effective search query.

### Example:
**Initial Query:** "events next Monday in New York"
**Current Date:** July 4, 2024
**Date of Next Monday:** July 8, 2024

### Optimized Query:**
events July 8, 2024 in New York
"""
    },
    {
        "role": "user",
        "content": """
Now, apply these steps to optimize the following query:

**Original Query:** {query}

Do not inclue the steps in the final output. The final output should be a single string of optimised query.
"""
    }
]

refine_prompt = [
    {
        "role": "system",
        "content": """
As a refining agent, your task is to evaluate and refine the returned search results from an optimized Google search query to ensure they meet the user's needs accurately and comprehensively. Follow these steps to refine the results:

1. **Analyze Initial Results:** Review the top results returned by the Google search. Each result is provided as a JSON object containing a link and a snippet. Pay close attention to these details.

2. **Relevance Check:** Assess each result for relevance to the original query. Ensure that the content directly addresses the user's intent and query requirements. Avoid discarding results that are partially relevant if they can still provide useful information.

3. **Authority and Credibility:** Evaluate the credibility of the sources. Prioritize results from authoritative, trustworthy, and relevant websites (e.g., .edu, .gov, established news sites, and reputable industry-specific sites).

4. **Content Quality:** Examine the quality of the content within the top results. Look for comprehensive, well-researched, and up-to-date information. Retain results that are partially relevant but provide valuable information that could be useful.

5. **Diversity of Perspectives:** Ensure a diversity of perspectives and information types are represented. Include results that offer different viewpoints, in-depth analyses, and various content formats (e.g., articles, videos, infographics).

6. **Filtering, Exclusion, and Redundancy Removal:** 
   - Remove any results that do not meet the criteria for relevance, credibility, and content quality.
   - Exclude results that are overly commercial, biased, or irrelevant.
   - Remove redundant results that provide identical or very similar information to ensure a variety of unique sources.

7. **Summarize Findings:** Provide a summary of the refined search results. Ensure the refined results are in the same format as the original results.

8. **Output Format:** Return the 10 most relevant results. Ensure the refined results are in the same format as the original results.
"""
    },
    {
        "role": "user",
        "content": """
Now, apply these steps to refine the returned search results for the following query:

**Original Query:** {query}

**Original Query Results:** {results}

Do not inclue the steps in the final output. The final output should be a single list of refined search results.
"""
    }
]