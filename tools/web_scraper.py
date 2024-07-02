from urllib.request import Request, urlopen
from io import BytesIO
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import json

def scrape_soup(url):
    """
    Parameters:
    url (str): The URL of the HTML-based webpage to scrape.

    Returns:
    str: The extracted text content from the webpage.
    """
    req = Request(
    url=url, 
    headers={'User-Agent': 'Mozilla/5.0'}
    )
    page = urlopen(req).read()
    soup = BeautifulSoup(page, "html.parser")

    title = soup.find('title')
    body = soup.find_all('p')
    text = title.get_text()
    for paragraph in body:
        text = '\n'.join([text, paragraph.get_text()])

    return text   

def scrape_pdf(url):
    """
    Scrapes text information from a given PDF page.

    Parameters:
    url (str): The URL of the PDF page to scrape.

    Returns:
    str: The extracted text content from the PDF page.
    """
    req = Request(
    url=url, 
    headers={'User-Agent': 'Mozilla/5.0'}
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
    extracted_texts = {}
    
    for url in urls:
        try:
            if url.endswith('.pdf'):
                extracted_text = scrape_pdf(url)
            else:
                extracted_text = scrape_soup(url)
            extracted_texts[url] = extracted_text
        except Exception as e:
            print(f"Error: Unable to access URL: {url}")
    
    return json.dumps(extracted_texts)
