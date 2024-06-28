from urllib import request
from io import BytesIO
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader

def scrape_webpage(url):
    """
    Parameters:
    url (str): The URL of the HTML-based webpage to scrape.

    Returns:
    str: The extracted text content from the webpage.
    """
    page = request.urlopen(url).read()
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
    remote_file = request.urlopen(url).read()
    memory_file = BytesIO(remote_file)
    reader = PdfReader(memory_file)
    num_of_pages = len(reader.pages)
    text = ""
    for page_num in range(num_of_pages):
        text = '\n'.join([text, reader.pages[page_num].extract_text()])

    return text

