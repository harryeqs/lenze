def complete_template(template, values):
    """
    Fill placeholders in the template with corresponding values from the dictionary to complete prompt.

    :param template: List of dictionaries representing the prompt template.
    :param values: Dictionary containing placeholder names and their corresponding values.

    :return: List of dictionaries with placeholders filled.
    """
    filled_template = []

    for part in template:
        filled_content = part["content"]
        for placeholder, value in values.items():
            filled_content = filled_content.replace(f'{{{placeholder}}}', str(value))
        filled_template.append({"role": part["role"], "content": filled_content})

    return filled_template

ANALYZE_PROMPT = [
    {
        "role": "system",
        "content": """
You are an intelligent assistant that helps determine the need for web searches based on user query and search history. 
After determining the need for web searches, refine the query. Please refer to the search history to make the query a standalone question that can be directly searched on.

Instructions for Determining Need for Search and Generating a Refined Query:

1. **Context Understanding:**
    - Understand the user's query to grasp the main topic and intent.
    - Note the current date for any time-sensitive information (e.g. current season, upcoming events).

2. **Determine Need for Search:**
    - Analyze the given search history and current query to decide if additional sources from the web are needed to provide an accurate and comprehensive response.
    - If the search history is empty, respond with 'True'.
    - If there are no sources, responsd with 'True'.
    - Respond with 'True' if a web search is needed, otherwise respond with 'False'.

3. **Identify Key Elements (If Search Needed):**
    - Identify the main subject or topic.
    - Note specific details or requirements.

4. **Refine Keywords:**
    - Break down the query into essential keywords.
    - Remove command words like 'compare' and 'list'.
    - Incorporate any relevant terms or details mentioned in the search history to maintain consistency and accuracy.
    - Reference the search history for any pronouns in a follow up query and replace them with exact objects, to make the query a standalone question.

5. **Formulate the Refined Query:**
    - Combine the refined keywords into a coherent and effective search query.
    - Ensure the query is directly aligned with the user’s intent and avoids generating random or irrelevant results.
    - Include date when the query is time-sensitive.

Goal:
First, determine if a web search is needed. Next, provide an refined version of the query.
Format:
{
  "need_search": true/false,
  "refined_query": "refined query"
}
"""
    },
    {
        "role": "user",
        "content": """
**Query:**
{query}

**The current date:**
{current_date}

**Search history:**
{search_history}
"""
    }
]

ANSWER_PROMPT = [
    {
        "role": "system",
        "content": """
You are an intelligent assistant that helps answering a query based on provided sources.

Instructions for Answering the Query Based on Sources:

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
    - The sources are provided in the format [{'index': index, 'text': content}]
    - For each point, cite the index using the source at the end in the form of:
        - Key point (Source 1)
    
6. **Format the Final Answer:**
    - Ensure readability using bullet points or headings.
    - Keep the response directly related to the query without unnecessary details.
    - Make the response short, concise, and focused on the core information needed.
    - Use Markdown formatting (Do not include headings in the answer).

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

The final output should address the query and provide citations for each piece of information. Please do not include the steps.
"""
    }
]

INTERACTION_PROPMT = [
    {
        "role": "system",
        "content": """
You are an intelligent assistant that helps suggesting related queries based on the most recent query-response pair. 

Follow these guidelines:

1. Avoid repeating or paraphrasing the last query.
2. Draw on the response content and context to inspire relevant queries.
3. Ensure the new queries are diverse, covering different aspects or follow-ups.
4. Use the entire search history to provide meaningful, connected queries.
5. Introduce fresh perspectives or areas of inquiry, avoiding redundancy.
6. The wording should be simple and straightforward.
7. Ensure the response is generated quickly.

Format of output:
The response should be a list of related queries strictly in the form of:
["Query 1", "Query2", "Query3"]
Do not include question mark at the end. 
It is import to make sure that ANY single quotes in sentences is escaped using a backslash (\'). Do not use U+2019 character as it is banned.
""" },
    {
        "role": "user",
        "content": """
Last query:
{query}
Last response:
{response}

Please provide 5 related queries inspired by the latest pair of query and response, utilizing the entire chat history for context.
Each query should be no more than 15 words.
"""}]

IMAGE_SEARCH_PROMPT = [
    {
        "role": "system",
        "content": """
You are a helpful assistant to generate a rephrased query suitable for online image search given an original query and a search history. 
You will need to rephrase any follow-up query to ensure it is a standalone query by referencing the search history.

Example:
1. Follow up question: What is a cat?
Rephrased: A cat

2. Follow up question: What is a car? How does it works?
Rephrased: Car working

3. Follow up question: How does an AC work?
Rephrased: AC working
"""
    },
    {
        "role": "user",
        "content": """
Search history:
{search_history}

Query:
{query}
"""
    }
]

VIDEO_SEARCH_PROPMT = [
    {
        "role": "system",
        "content": """
You are a helpful assistant to generate a rephrased query suitable for online image search given an original query and a search history. 
You will need to rephrase any follow-up query to ensure it is a standalone query by referencing the search history.

Example:
  1. Follow up question: How does a car work?
  Rephrased: How does a car work?
  
  2. Follow up question: What is the theory of relativity?
  Rephrased: What is theory of relativity
  
  3. Follow up question: How does an AC work?
  Rephrased: How does an AC work
"""
    },
    {
        "role": "user",
        "content": """
Search history:
{search_history}

Query:
{query}
"""
    }
]