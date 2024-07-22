from bs4 import BeautifulSoup
import requests, json, random
from googleapiclient.discovery import build
import os
import json
from dotenv import load_dotenv

def google_scrape_search(query: str, num: int = 10):
    """
    Conduct a google search on a given query.
    
    :param query: The query to be searched.
    :type query: str
    :param num: The number of results.
    :type num: int (optional)
    :return: A JSON array of search results.
    :rtype: JSON array
    """
    # https://docs.python-requests.org/en/master/user/quickstart/#passing-parameters-in-urls
    params = {
        "q": query, # query example
        "hl": "",          # language
        "gl": "",          # country of the search, UK -> United Kingdom
        "start": 0,          # number page by default up to 0         # parameter defines the maximum number of results to return.
    }

    # https://docs.python-requests.org/en/master/user/quickstart/#custom-headers
    user_agent_list = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    ]

    for _ in user_agent_list:
        #Pick a random user agents
        user_agent = random.choice(user_agent_list)

        #Set the headers 
        headers = {'User-Agent': user_agent}

    results = []

    while len(results) < num:
            
        html = requests.get("https://www.google.com/search", params=params, headers=headers, timeout=30)
        soup = BeautifulSoup(html.text, 'lxml')
        
        for result in soup.select(".tF2Cxc"):
            title = result.select_one(".DKV0Md").text
            link = result.select_one(".yuRUbf a")["href"]
        
            results.append({
            "title": title,
            "link": link
            })

        if not soup.select_one(".d6cvqb a[id=pnnext]"):
            break

        params["start"] += 10

    return json.dumps(results[:num], indent=2)

def get_urls(results):
    results = json.loads(results)
    urls = [result['link'] for result in results]
    return urls


# Load the environment variables from the .env file
load_dotenv()
my_api_key = os.getenv('GOOGLE_API_KEY')
my_cse_id = os.getenv('CSE_ID')

def google_api_search(search_term, api_key=my_api_key, cse_id=my_cse_id, attempts=3, **kwargs):
    """ 
    Conduct a Google search on a given search term.

    Parameters: 
    search_term (str): The term to be searched.

    Returns:
    list: a list of dictionaries each containing a link to the search result and a snippet of the result.

    """
    service = build("customsearch", "v1", developerKey=api_key)

    for attempt in range(attempts):
        try:
            request = service.cse().list(
                q=search_term,
                cx=cse_id,
                safe=kwargs.get('safe', 'off'),
                cr=kwargs.get('cr', ''),             # Country restriction
                gl=kwargs.get('gl', ''),             # Geolocation
                lr=kwargs.get('lr', ''),             # Language restriction
                filter=kwargs.get('filter', ''),    # Duplicate content filter
                c2coff=kwargs.get('c2coff', ''),    # Translation setting
                hl=kwargs.get('hl', ''),             # Interface language
                siteSearch=kwargs.get('siteSearch', '')  # Site restriction
            )
            # print(f"\nRequest parameters: {request.uri}")  # Debug: log the request parameters
            res = request.execute()
            if 'items' in res:
                full_results = res['items']
                results = [{'link': result['link']} for result in full_results]
                return json.dumps(results)
            else:
                print(f"\nNo search results found. Attempt {attempt + 1} of {attempts}.")
        except Exception as e:
            print(f"An error occurred: {e}. Attempt {attempt + 1} of {attempts}.")
    
    print("\nNo search results found after all attempts.")
    return json.dumps([])