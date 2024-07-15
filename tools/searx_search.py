import time
from langchain_community.utilities import SearxSearchWrapper

search = SearxSearchWrapper(searx_host="http://127.17.0.2:80/")

def searx(query, num_of_results=10, max_retries=3, initial_delay=1):
    """
    Search using SearXNG with retry mechanism.

    Parameters:
    query (str): The query to be searched.
    num_of_results (int): The number of results required.
    max_retries (int): Maximum number of retries if rate limited.
    initial_delay (int): Initial delay between retries in seconds.
    """
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            results = search.results(query, num_results=num_of_results)
            return results
        except Exception as e:
            if 'Too Many Requests' in str(e):
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise e
    raise Exception("Too Many Requests. Max retries exceeded.")


try:
    results = searx("Eurocup")
    print(results)
except Exception as e:
    print(f"An error occurred: {e}")