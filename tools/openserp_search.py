import requests

class OpenSERPAPI:
    def __init__(self, base_url="http://127.0.0.1:7000"):
        self.base_url = base_url

    def search(self, engine, query, **params):
        endpoint = f"{self.base_url}/{engine}/search"
        params["text"] = query
        response = requests.get(endpoint, params=params)
        return response.json()

    def image_search(self, engine, query, **params):
        endpoint = f"{self.base_url}/{engine}/image"
        params["text"] = query
        response = requests.get(endpoint, params=params)
        return response.json()

# Usage example
api = OpenSERPAPI()

# Perform a Google search
results = api.search("google", "llm", limit=10)
for result in results:
    print(result)
