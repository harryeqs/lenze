import requests
from bs4 import BeautifulSoup
import fitz
from io import BytesIO
import aiohttp
import asyncio
import time

async def scrape_soup_async(url, session, retries=2, timeout=2, max_content=3000):
    """
    Scrapes text content from an HTML-based page.

    Parameters:
    url (str): The URL of the HTML-based webpage to scrape.

    Returns:
    str: The extracted text content from the webpage.
    """
    while retries > 0:
        try:
            async with session.get(url, timeout=timeout) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(f"Failed to fetch {url}, status code: {response.status}")
                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")
                main_content = soup.find('main') or soup.find('article') or soup.body
                
                text = ""
                if main_content:
                    title = soup.find('title').get_text() if soup.find('title') else ""
                    paragraphs = main_content.find_all('p')
                    text = title
                    for paragraph in paragraphs:
                        text += '\n' + paragraph.get_text()
                return text[:max_content]
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Error: Unable to access URL: {url}. Exception: {e}. Retries left: {retries-1}")
        retries -= 1
        await asyncio.sleep(1)  # Backoff before retrying
    return ""

def scrape_pdf(url, retries=2, timeout=2, max_content=5000):
    """
    Scrapes text content from a given PDF page.

    Parameters:
    url (str): The URL of the PDF page to scrape.

    Returns:
    str: The extracted text content from the PDF page.
    """
    while retries > 0:
        try:
            response = requests.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type')
                if content_type != 'application/pdf':
                    raise ValueError("The URL does not point to a PDF file.")
                
                remote_file = response.content
                memory_file = BytesIO(remote_file)
                pdf_document = fitz.open(stream=memory_file, filetype='pdf')

                text = ""
                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    text += page.get_text()

                return text[:max_content]
        except requests.RequestException as e:
            print(f"RequestException: Unable to access URL: {url}. Reason: {e}. Retries left: {retries-1}")
        retries -= 1
        time.sleep(1)  # Backoff before retrying    
    return ""

async def scrape_url_async(url, session):
    """
    Scrapes text content from a single URL asynchronously.

    Parameters:
    url (str): The URL to scrape.
    session (aiohttp.ClientSession): The aiohttp session.

    Returns:
    str: The extracted text content.
    """
    try:
        if url.lower().endswith('.pdf') or ('/pdf/' in url):
            return scrape_pdf(url)
        else:
            return await scrape_soup_async(url, session)
    except Exception as e:
        print(f"Exception: Unable to access URL: {url}. Exception: {e}")
    return ""

async def scrape_urls_async(urls):
    """
    Scrapes text content from a list of URLs asynchronously.

    Parameters:
    urls (list): The list of URLs to scrape.

    Returns:
    list: The list of extracted text content from each URL.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_url_async(url, session) for url in urls]
        return await asyncio.gather(*tasks)

def scrape_urls(urls):
    """
    Wrapper function to run the async scraper.

    Parameters:
    urls (list): The list of URLs to scrape.

    Returns:
    list: The list of extracted text content from each URL.
    """
    return asyncio.run(scrape_urls_async(urls))

