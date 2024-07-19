import requests
from bs4 import BeautifulSoup

query = 'apple vision pro price china'
response = requests.get(f"https://www.google.com/search?q={query}") # Make the request
soup = BeautifulSoup(response.text, "html.parser") # Parse the HTML
links = soup.find_all("a") # Find all the links in the HTML

print(links)