from urllib.request import Request, urlopen
from urllib import error
from io import BytesIO
from bs4 import BeautifulSoup
from selenium import webdriver
import fitz
import time

def scrape_soup(url, retries=3, timeout=3, max_content = 3000):
    """
    Scrapes text content from an HTML-based page.

    Parameters:
    url (str): The URL of the HTML-based webpage to scrape.

    Returns:
    str: The extracted text content from the webpage.
    """
    while retries > 0:
        try:
            driver = webdriver.Chrome()
            driver.set_page_load_timeout(timeout)  
            driver.get(url)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            title = soup.find('title')
            body = soup.find_all('p')
            text = title.get_text()
            
            for paragraph in body:
                text = '\n'.join([text, paragraph.get_text()])
            return text[:max_content]
        except error.URLError as e:
            print(f"URLError: Unable to access URL: {url}. Reason: {e.reason}. Retries left: {retries-1}")
        except Exception as e:
            print(f"Exception: An unexpected error occurred while accessing URL: {url}. Exception: {e}. Retries left: {retries-1}")
        retries -= 1
        time.sleep(1)  # Backoff before retrying
    return ""  # Return None if all retries fail   

def scrape_pdf(url, retries=3, timeout=3, max_content = 5000):
    """
    Scrapes text content from a given PDF page.

    Parameters:
    url (str): The URL of the PDF page to scrape.

    Returns:
    str: The extracted text content from the PDF page.
    """

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
    """
    while retries > 0:
        try:
            req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36'})
            with urlopen(req, timeout=timeout) as response:
                content_type = response.info().get_content_type()
                if content_type != 'application/pdf':
                    raise ValueError("The URL does not point to a PDF file.")
                
                remote_file = response.read()
                memory_file = BytesIO(remote_file)
                pdf_document = fitz.open(stream=memory_file, filetype='pdf')

                text = ""
                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    text += page.get_text()

                return text[:max_content]

        except error.URLError as e:
            print(f"URLError: Unable to access URL: {url}. Reason: {e.reason}. Retries left: {retries-1}")
        except Exception as e:
            print(f"Exception: An unexpected error occurred while accessing URL: {url}. Exception: {e}. Retries left: {retries-1}")
        retries -= 1
        time.sleep(1)  # Backoff before retrying    

        return ""



def is_pdf(url):
    """
    Checks if the URL points to a PDF document by making a HEAD request.

    Parameters:
    url (str): The URL to check.

    Returns:
    bool: True if the URL points to a PDF document, False otherwise.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        req = Request(url, headers=headers, method='HEAD')
        with urlopen(req) as response:
            content_type = response.info().get_content_type()
            return content_type == 'application/pdf'
    except error.URLError as e:
        print(f"An error occurred while checking the URL: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    

def scrape_url(url):

    """
    Scrapes text contents from a list of URLs.

    Parameters:
    url (str): The URL to scrape.

    Returns:
    str: The extracted text content.
    """
    
    try:
        if url.lower().endswith('.pdf') or is_pdf(url):
            extracted_text = scrape_pdf(url)
        else:
            extracted_text = scrape_soup(url)
        
        if not extracted_text:
            print(f"\nFailed to scrape URL after retries: {url}")
    except Exception as e:
        print(f"\nError: Unable to access URL: {url}. Exception: {e}")
    
    return extracted_text