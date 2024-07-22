CHECK_SEARCH_PROMPT = [
    {"role": "system", "content": "You are an intelligent assistant that helps determine the need for web searches based on user queries and search history."},
    {"role": "user", "content": "Analyze the given search history and current query. Determine if additional sources from the web are needed to provide an accurate and comprehensive response. If the search history is empty, you must respond with 'True'. Respond with 'True' if a web search is needed, otherwise respond with 'False'."},
    {"role": "user", "content": "Search history: {search_history}\nQuery: {query}"}
]

ANALYZE_PROMPT = [
    {
        "role": "system",
        "content": """
As a helpful assistant, your task is to analyze the user's query, break it down into simpler, concise sub-queries if necessary, and then refine and optimize these sub-queries for the most accurate and relevant results on Google.

Instructions for Analyzing and Optimizing User Query:

1. **Context Understanding:**
    - Understand the user's query to grasp the main topic and intent.
    - Note the current date for any time-sensitive information.

2. **Identify Key Elements:**
    - Identify the main subject or topic.
    - Note specific details or requirements.

3. **Decompose into Sub-Queries Only When Necessary:**
    - Generate sub-queries only if the original query covers multiple distinct aspects that need separate searches.
    - Ensure sub-queries are concise and cover clearly different facets of the main query.
    - Align sub-queries with the original query's context and requirements.
    - Limit the number of sub-queries to the minimum necessary to comprehensively address the query (ideally no more than three).

4. **Avoid Redundancy and Irrelevance:**
    - Ensure each sub-query addresses a distinctly different aspect of the main query.
    - Avoid sub-queries that are similar, overlapping, or loosely related to the main query.
    - Ensure sub-queries do not introduce new topics not explicitly asked for in the main query.

5. **Incorporate Temporal Context:**
    - Explicitly include the current date or relevant time period (e.g., seasons, festivals) in the sub-queries if the query is time-sensitive.
    - For example, if the query is about something 'currently in season', identify and incorporate the current season in sub-queries.

6. **Refine Keywords:**
    - Break down each sub-query into essential keywords.
    - Remove command words like 'compare' and 'list'.
    - Add or modify keywords to include synonyms, related terms, and variations that capture the full scope of the user’s intent.
    - Incorporate any relevant terms or details mentioned in the search history to maintain consistency and accuracy.

7. **Use Operators:**
    - Utilize Google search operators to narrow down the results only when necessary:
      - Use the minus sign (-) to exclude unwanted terms.
      - Use the filetype: operator to find specific types of files (e.g., PDFs, DOCs).
      - Use the intitle: operator to ensure the main keyword appears in the title of the results (only when necessary).
    - *Important*: DO NOT use quotation marks or site operators.

8. **Formulate the Optimized Query:**
    - Combine the refined keywords, operators, and filters into a coherent and effective search query.
    - Ensure the query is directly aligned with the user’s intent and avoids generating random or irrelevant results.

Goal:
Provide a list of sub-queries (if needed), each followed by its optimized version for web search.
"""
    },
    {
        "role": "user",
        "content": """
Now, apply these steps and analyze and optimize the query:

**Query:**
{query}

**The current date:**
{current_date}

**Search history:**
{search_history}

The output should be a list of optimized version of sub-queries.
Format:
["optimized query 1", "optimized query 2"]
"""
    }
]

ANSWER_PROMPT = [
    {
        "role": "system",
        "content": """
1. **Understand the Query:**
    - Read the user's original query carefully.
    - Identify the core question and key details.

2. **Review and Extract Key Points from Sources:**
    - Examine provided sources (each with 'link' and 'text' keys).
    - Extract only information directly answering the user's query. Do not include additional details.
    - Use various sources for comprehensive information.
    - Ignore extraneous or unrelated content.

3. **Organize Extracted Information:**
    - Group related information logically.
    - Ensure a clear and comprehensive flow.

4. **Compose a Focused Answer:**
    - Write a concise, clear response.
    - Integrate extracted information seamlessly.
    - Provide accurate, short points instead of lengthy explanations.
    - Do not provide additional details not asked explicitly in the original query.

5. **Cite Sources Appropriately:**
    - Index only the sources that have been used in the format, place it at the end of the answer in the following format:
        **Sources**
        - Source 1: website-name (full-url)
        - Source 2: website-name (full-url) 
    - Cite each piece of information in the answer strictly in the format (Source <index>), where <index> corresponds to the index of the source.
    - Please re-index the sources for each new answer.
    
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
Based on the following sources, please respond to the query comprehensively and cite each source for the information provided.
**Query:** {query}

**Sources:**
{sources}

The final output should address the query and provide citations for each piece of information strictly in the required format. Please do not include the steps.
Ensure that the link to the source is included in the citation.
"""
    }
]

INTERACTION_PROPMT = [
    {
        "role": "system",
        "content": """
As a helpful assistant, your task is to suggest related queries based on the most recent query-response pair. Follow these guidelines:

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