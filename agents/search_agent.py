__all__ = ["SearchAgent"]

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent
from tools.google_search import google_search
from tools.web_scraper import scrape_urls
from tools.data_store import local_store
from datetime import datetime
import json

class SearchAgent(Agent):

    def __init__(self, llm_client: OpenAIClient):
        super().__init__()

        self.set_information(
            {
                "type": "function",
                "function": {
                    "name": "SearchAgent",
                    "description": "This agent can search across the internet on a sub-query provided by the user by following the searching process and return a list of raw source data. To be called only once.",

                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sub_queries": {"type": "array", 
                                            "items": {"type": "string"}, 
                                            "description": "The sub-queries here which need help. It should passed to the next agent it its original form."},
                            "current_date": {"type": "string", "description": "The current date."}
                        },
                        "required": ["sub_queries", "current_date"],
                    },
                }
            }
        )
        self.input_type = "str"
        self.output_type = "list"

        self.opt_agent = LLMAgent(template=opt_prompt, llm_client=llm_client, stream=False)
        self.refine_agent = LLMAgent(template=refine_prompt, llm_client=llm_client, stream=False)

    def flowing(self, sub_queries: list, current_date = None):
        
        # Initialise counter

        # Get current time
        current_date = datetime.today()
        yield (f'**The current time is:** {current_date}' +
              f'\n --------------------')
        
        for sub_query in sub_queries:
            # Generate optimised query
            opt_query = self.opt_agent(sub_query=sub_query, current_date=current_date)
            yield (f'\n**Optimized query:** \n {opt_query}' +
                f'\n --------------------')
        
            # Search using optimised query
            results = google_search(opt_query)
            yield (f'\n**Search results:** \n {results}' +
                f'\n --------------------')

            # Refine the search results
            refined_results = self.refine_agent(sub_query=sub_query, results=results)
            yield (f'\n**Refined results:** {refined_results}' +
                f'\n --------------------')
            results =json.loads(refined_results)

            # scrape URLs contained in search results and returned compiled sources
            
            yield ('\n**Scraping texts from refined results.**')

            urls = [result['link'] for result in results]
            scraped_texts = scrape_urls(urls)

            sources = []
            counter = 1

            for result, text in zip(results, scraped_texts):
                result['text'] = text
                result.pop('snippet')
                sources.append({f'source-{counter}': result})
                counter += 1
            
            local_store(sources)

            yield (f"\n**Sources for sub-query '{sub_query}' stored locally, proceed to next step.**\n")
    


opt_prompt = [
    {
        "role": "system",
        "content": """
As an intelligent search optimization agent, your task is to refine and optimize a given query to achieve the most accurate and relevant results on Google. Follow these steps to enhance the query and ensure precision:

Steps to Optimize the Query:

1. **Understand the Query:**
   - Analyze the initial query to grasp the key concepts and the user’s intent.
   - Identify the main topic, specific details, and any implicit or explicit requirements.

2. **Refine Keywords:**
   - Break down the query into essential keywords.
   - Add or modify keywords to include synonyms, related terms, and variations that capture the full scope of the user’s intent.

3. **Use Operators:**
   - Utilize Google search operators to narrow down the results only when necessary:
     - Use the minus sign (-) to exclude unwanted terms.
     - Use the filetype: operator to find specific types of files (e.g., PDFs, DOCs).
     - Use the intitle (only when necessary): operator to ensure the main keyword appears in the title of the results.
   - *Important*: DO NOT use quotation marks or sites.

4. **Incorporate Filters:**
   - Add filters like location, date range, or language to make the search results more relevant.
   - For example, add “2024” to find the most recent information or specify “site:.edu” or "site:.ac.*" for educational resources.

5. **Special Case Handling:**
   - For date-specific queries, such as “events next Monday,” automatically determine the date based on the **current date:** {current_date} and incorporate it into the search query.

6. **Formulate the Optimized Query:**
   - Combine the refined keywords, operators, and filters into a coherent and effective search query.
   - Ensure the query is directly aligned with the user’s intent and avoids generating random or irrelevant results.

**Emphasis:**
   - Check the current time and make sure the information is up to date.

Goal:
Create a search query that maximizes accuracy and relevance, aligning with the user’s intent and providing the best possible results.
""" },
    {
        "role": "user",
        "content": """
Now, apply these steps to optimize the following query:

**Sub-query:** {sub_query}

Do not inclue the steps in the final output. The final output should be a single string of optimised query.
"""
    }
]

refine_prompt = [
    {
        "role": "system",
        "content": """
As a refining agent, your task is to evaluate and refine the returned search results from an optimized Google search query to ensure they meet the user's needs accurately and comprehensively. Follow these steps to refine the results:

1. **Analyze Initial Results:** 
    - Review the top results returned by the Google search.
    - Each result is provided as a JSON object containing a link and a snippet. Pay close attention to these details.

2. **Relevance Check:** 
    - Assess each result for relevance to the original query.
    - Avoid discarding results that are partially relevant if they can still provide useful information.
    - **Important:** Please keep the results even if they are not exact match.

3. **Authority and Credibility:** 
    - Evaluate the credibility of the sources. Prioritize results from authoritative, trustworthy, and relevant websites (e.g., .edu, .gov, established news sites, and reputable industry-specific sites).

4. **Content Quality:** 
    - Examine the quality of the content within the top results. 
    - Look for comprehensive, well-researched, and up-to-date information. 
    - Retain results that are partially relevant but provide valuable information that could be useful.

5. **Diversity of Perspectives:** 
    - Ensure a diversity of perspectives and information types are represented. 
    - Include results that offer different viewpoints, in-depth analyses, and various content formats (e.g., articles, videos, infographics).

6. **Filtering, Exclusion, and Redundancy Removal:** 
   - Remove any results that do not meet the criteria for relevance, credibility, and content quality.
   - Exclude results that are overly commercial, biased, or irrelevant.
   - Remove redundant results that provide identical or very similar information to ensure a variety of unique sources.

7. **Output Format:** Return the 5 most relevant results at maximum. Ensure the refined results are in the same format as the original results.

**Important**: ALWAYS remind yourself of the current sub query.
"""
    },
    {
        "role": "user",
        "content": """
Now, apply these steps to refine the returned search results for the following query:

**Sub-query:** {sub_query}

**Sub-query Results:** {results}

Do not inclue the steps in the final output. The final output should be a single list of refined search results only. Do not include any explanation or narration.
"""
    }
]