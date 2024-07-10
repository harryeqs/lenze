from langchain_community.utilities import SearxSearchWrapper

search = SearxSearchWrapper(searx_host="http://127.0.0.1:8888")

def searx(query, num_of_results=10):
    """
    Search using SearXNG.

    Parameters:
    query (str): The qeury to be searched.
    num_of_results (int): The number of results required.
    """
    results = search.results(query, num_results=num_of_results)
    return results