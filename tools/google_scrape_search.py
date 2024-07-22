from bs4 import BeautifulSoup
import requests, json, random

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


if __name__ == '__main__':
    results = google_search('why is the sky blue')
    print(results)