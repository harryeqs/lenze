import os
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build

def get_urls(results):
    results = json.loads(results)
    urls = [result['link'] for result in results]
    return urls

# Load the environment variables from the .env file
load_dotenv()
my_api_key = os.getenv('GOOGLE_API_KEY')
my_cse_id = os.getenv('CSE_ID')

def web_search(search_term, api_key = my_api_key, cse_id = my_cse_id, num=10, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    all_links = []
    start = 1
    while start < num:
        res = service.cse().list(q=search_term, cx=cse_id, start=start, num=10, **kwargs).execute()
        start += 10
        links = get_urls(json.dumps(res['items']))
        all_links.extend(links)

    return all_links[:num]
