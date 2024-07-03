from urllib.request import Request, urlopen
from urllib import error
from io import BytesIO
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import json
import time

def scrape_soup(url, retries=3, timeout=2):
    """
    Scrapes text content from an HTML-based page.

    Parameters:
    url (str): The URL of the HTML-based webpage to scrape.

    Returns:
    str: The extracted text content from the webpage.
    """
    while retries > 0:
        try:
            req = Request(
            url=url, 
            headers={'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36'}
            )
            page = urlopen(req, timeout=timeout).read()
            soup = BeautifulSoup(page, "html.parser")

            title = soup.find('title')
            body = soup.find_all('p')
            text = title.get_text()
            for paragraph in body:
                text = '\n'.join([text, paragraph.get_text()])
            return text
        except error.URLError as e:
            print(f"URLError: Unable to access URL: {url}. Reason: {e.reason}. Retries left: {retries-1}")
        except Exception as e:
            print(f"Exception: An unexpected error occurred while accessing URL: {url}. Exception: {e}. Retries left: {retries-1}")
        retries -= 1
        time.sleep(2)  # Backoff before retrying
    return None  # Return None if all retries fail   

def scrape_pdf(url):
    """
    Scrapes text content from a given PDF page.

    Parameters:
    url (str): The URL of the PDF page to scrape.

    Returns:
    str: The extracted text content from the PDF page.
    """
    req = Request(
    url=url, 
    headers={'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36'}
    )
    remote_file = urlopen(req).read()
    memory_file = BytesIO(remote_file)
    reader = PdfReader(memory_file)
    num_of_pages = len(reader.pages)
    text = ""
    for page_num in range(num_of_pages):
        text = '\n'.join([text, reader.pages[page_num].extract_text()])

    return text

def scrape_urls(urls):
    sources = {}

    """
    Scrapes text contents from a list of URLs.

    Parameters:
    urls (list): The list of URLs to scrape.

    Returns:
    str: A dictionary of sources, containing URLs and corresponding extracted texts.
    """
    
    for i in range(len(urls)):
        url = urls[i]
        try:
            if url.endswith('.pdf'):
                extracted_text = scrape_pdf(url)
            else:
                extracted_text = scrape_soup(url)
            
            if extracted_text:
                print(extracted_text)
                sources[f"source-{i+1}"] = {"url": url, "text": extracted_text}
            else:
                print(f"Failed to scrape URL after retries: {url}")
        except Exception as e:
            print(f"Error: Unable to access URL: {url}")
    
    return json.dumps(sources)


if __name__ == "__main__":
    scrape_urls(["https://www.accuweather.com/en/cn/shenzhen/58194/weather-forecast/58194", "https://weather.com/weather/tenday/l/7a4684e0789c881e79935986f2e9e5ab05b0104ac4310fd8818006dfb66092c3", "https://www.timeanddate.com/weather/china/shenzhen/ext"])