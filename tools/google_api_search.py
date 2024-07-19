from googleapiclient.discovery import build
import os
import json
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()
my_api_key = os.getenv('GOOGLE_API_KEY')
my_cse_id = os.getenv('CSE_ID')

def google_search(search_term, api_key=my_api_key, cse_id=my_cse_id, attempts=3, **kwargs):
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
            print(f"\nRequest parameters: {request.uri}")  # Debug: log the request parameters
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


if __name__ == "__main__":
    kwargs = {
        'gl': 'uk',
        'hl': 'en',
        'lr': 'lang_en'

    }
    results = google_search('apple vision pro price china', **kwargs)
    print(results)
    print (len(results))