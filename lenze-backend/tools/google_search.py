import os
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build

def get_sources(results):
    results = json.loads(results)
    sources = [{'title': result['title'], 'link': result['link']} for result in results]
    return sources

# Load the environment variables from the .env file
load_dotenv()
my_api_key = os.getenv('GOOGLE_API_KEY')
my_cse_id = os.getenv('CSE_ID')

def web_search(search_term, api_key = my_api_key, cse_id = my_cse_id, num=10, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    full_sources = []
    start = 1
    while start < num:
        res = service.cse().list(q=search_term, cx=cse_id, start=start, num=10, **kwargs).execute()
        start += 10
        sources = get_sources(json.dumps(res['items']))
        full_sources.extend(sources)

    return full_sources[:num]
