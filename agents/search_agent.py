__all__ = ["SearchAgent"]

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent
from tools.google_search import google_search

class SearchAgent(Agent):

    def __init__(self, llm_client: OpenAIClient):
        super().__init__()

        self.set_information(
            {
                "type": "function",
                "function": {
                    "name": "SearchAgent",
                    "description": "This agent can search across the internet on a query provided by the user by following the searching process.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "The query here which need help."}
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

        # Search using optimised query
        results = google_search(opt_query)

        # Refine the results
        refined_results = self.refine_agent(query=query, results=results)

        return refined_results
    

opt_prompt = [
    {
        "role": "system",
        "content": """
As an intelligent search optimization agent, your task is to refine and optimize a given query to achieve the most accurate and relevant results on Google. Follow these steps to enhance the query:

1. **Understand the Query:** Analyze the initial query to understand the key concepts and the user's intent. Identify the main topic, specific details, and any implicit or explicit requirements.

2. **Refine Keywords:** Break down the query into essential keywords. Add or modify these keywords to include synonyms, related terms, and variations that capture the full scope of the user's intent.

3. **Use Operators:** Utilize Google search operators to narrow down the results. This includes:
   - Quotation marks ("") to search for exact phrases.
   - The minus sign (-) to exclude unwanted terms.
   - The site: operator to limit results to a specific website or domain.
   - The filetype: operator to find specific types of files (e.g., PDFs, DOCs).
   - The intitle: operator to ensure the main keyword is in the title of the results.

4. **Incorporate Filters:** Consider adding filters like location, date range, or language to make the search results more relevant. For example, adding "2024" to find the most recent information or specifying "site:.edu" for educational resources.

5. **Formulate the Optimized Query:** Combine the refined keywords, operators, and filters into a coherent and effective search query.

### Example:
Initial Query: "best restaurants in New York"

1. **Understand the Query:** The user is looking for top-rated dining options in New York City.
2. **Refine Keywords:** Best, top-rated, restaurants, dining options, New York City, NYC.
3. **Use Operators:** "best restaurants" "New York City" -cheap -fast food.
4. **Incorporate Filters:** Add "2024" for the most recent results, "site:.com" for commercial sites.
5. **Formulate the Optimized Query:** "best restaurants" "New York City" 2024 -cheap -fast food site:.com.
6. **Test and Iterate:** Perform the search and adjust based on the results.
"""
    },
    {
        "role": "user",
        "content": """
Now, apply these steps to optimize the following query:

**Initial Query:** {query}
"""
    }
]

refine_prompt = [
    {
        "role": "system",
        "content": """
As a refining agent, your task is to evaluate and refine the returned search results from an optimized Google search query to ensure they meet the user's needs accurately and comprehensively. Follow these steps to refine the results:

1. **Analyze Initial Results:** Review the top results returned by the Google search. Each result is provided as a JSON object containing a link and a snippet. Pay close attention to these details.

2. **Relevance Check:** Assess each result for relevance to the original query. Ensure that the content directly addresses the user's intent and query requirements. 

3. **Authority and Credibility:** Evaluate the credibility of the sources. Prioritize results from authoritative, trustworthy, and relevant websites (e.g., .edu, .gov, established news sites, and reputable industry-specific sites).

4. **Content Quality:** Examine the quality of the content within the top results. Look for comprehensive, well-researched, and up-to-date information. Discard results that contain outdated, shallow, or irrelevant content.

5. **Diversity of Perspectives:** Ensure a diversity of perspectives and information types are represented. Include results that offer different viewpoints, in-depth analyses, and various content formats (e.g., articles, videos, infographics).

6. **Filtering and Exclusion:** Remove any results that do not meet the criteria for relevance, credibility, and content quality. Exclude results that are overly commercial, biased, or irrelevant.

7. **Summarize Findings:** Provide a summary of the refined search results. Include a brief description of each selected result, explaining why it was chosen and how it addresses the original query. Ensure the refined results are in the same format as the original results.

### Example:
**Original Query:** "best restaurants in New York City 2024 -cheap -fast food site:.com"
**Initial Results Review:**
1. **Result 1:**
   - **Link:** "https://example.com/top-10-restaurants-nyc-2024"
   - **Snippet:** "Top 10 Restaurants in NYC for 2024 - The Ultimate Guide"
   - Relevance: High
   - Credibility: High (reputable food blog)
   - Content Quality: High (detailed reviews, up-to-date)
   - Diversity: Comprehensive list with different cuisines

2. **Result 2:**
   - **Link:** "https://example.com/nyc-dining-guide-2024"
   - **Snippet:** "NYC Dining Guide 2024: Best Spots for Fine Dining"
   - Relevance: High
   - Credibility: Medium (general lifestyle site)
   - Content Quality: Medium (less detailed but useful)
   - Diversity: Focus on fine dining

**Refined Results Summary:**
1. **Link:** "https://example.com/top-10-restaurants-nyc-2024"
   - **Snippet:** "Top 10 Restaurants in NYC for 2024 - The Ultimate Guide"
   - **Reason:** Chosen for its detailed and comprehensive reviews of various cuisines.

2. **Link:** "https://example.com/nyc-dining-guide-2024"
   - **Snippet:** "NYC Dining Guide 2024: Best Spots for Fine Dining"
   - **Reason:** Included for its focus on fine dining options, adding diversity to the recommendations.
"""
    },
    {
        "role": "user",
        "content": """
Now, apply these steps to refine the returned search results for the following query:

**Original Query:** {query}

**Original Query Results:** {results}
"""
    }
]