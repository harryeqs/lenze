from googleapiclient.discovery import build
import pprint
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()
my_api_key = os.getenv('GOOGLE_API_KEY')
my_cse_id = os.getenv('CSE_ID')

def google_search(search_term, api_key=my_api_key, cse_id=my_cse_id, **kwargs):
    """ 
    Conduct a Google search on a given search term.

    Parameters: 
    search_term (str): The term to be searched.

    Returns:
    list: a list of urls where the answers can be found.

    """
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    results = res['items']
    sources = [result['link'] for result in results]
    return sources