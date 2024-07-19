from bs4 import BeautifulSoup
import requests, json

def google(query: str, num: int = 10):
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
        "hl": "en",          # language
        "gl": "uk",          # country of the search, UK -> United Kingdom
        "start": 0,          # number page by default up to 0         # parameter defines the maximum number of results to return.
    }

    # https://docs.python-requests.org/en/master/user/quickstart/#custom-headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }

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


