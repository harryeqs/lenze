import requests
from bs4 import BeautifulSoup
import fitz
from io import BytesIO
import asyncio
import time
from typing import List
from playwright.async_api import async_playwright

async def scrape_js_rendered_page(url: str, wait_time: int = 5, max_content: int = 5000) -> str:
    """
    Scrapes text content from a JavaScript-rendered web page using Playwright.

    Parameters:
    url (str): The URL of the web page to scrape.
    wait_time (int): Time in seconds to wait for the page to load JavaScript content.
    max_content (int): Maximum content length to return.

    Returns:
    str: The extracted text content from the webpage.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(wait_time)
        html_content = await page.content()
        await browser.close()

    soup = BeautifulSoup(html_content, "html.parser")
    main_content = soup.find('main') or soup.find('article') or soup.body
    
    text = ""
    if main_content:
        title = soup.find('title').get_text() if soup.find('title') else ""
        paragraphs = main_content.find_all('p')
        text = title
        for paragraph in paragraphs:
            text += '\n' + paragraph.get_text()
    return text[:max_content]

def scrape_pdf(url: str, retries: int = 2, timeout: int = 2, max_content: int = 5000) -> str:
    """
    Scrapes text content from a given PDF page.

    Parameters:
    url (str): The URL of the PDF page to scrape.
    retries (int): Number of retries in case of failure.
    timeout (int): Timeout for the request.
    max_content (int): Maximum content length to return.

    Returns:
    str: The extracted text content from the PDF page.
    """
    while retries > 0:
        try:
            response = requests.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code != 200:
                raise requests.RequestException(f"Failed to fetch {url}, status code: {response.status}")
            
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
            print(f"RequestException: Unable to access URL: {url}. Reason: {e}. Retries left: {retries - 1}")
        retries -= 1
        time.sleep(1)  # Backoff before retrying    
    return ""

async def scrape_url_async(url: str) -> str:
    """
    Scrapes text content from a single URL asynchronously.

    Parameters:
    url (str): The URL to scrape.

    Returns:
    str: The extracted text content.
    """
    try:
        if url.lower().endswith('.pdf') or ('/pdf/' in url):
            return scrape_pdf(url)
        else:
            return await scrape_js_rendered_page(url)
    except Exception as e:
        print(f"Exception: Unable to access URL: {url}. Exception: {e}")
    return ""

async def scrape_urls_async(urls: List[str]) -> List[str]:
    """
    Scrapes text content from a list of URLs asynchronously.

    Parameters:
    urls (list): The list of URLs to scrape.

    Returns:
    list: The list of extracted text content from each URL.
    """
    tasks = [scrape_url_async(url) for url in urls]
    return await asyncio.gather(*tasks)

def scrape_urls(urls: List[str]) -> List[str]:
    """
    Wrapper function to run the async scraper.

    Parameters:
    urls (list): The list of URLs to scrape.

    Returns:
    list: The list of extracted text content from each URL.
    """
    return asyncio.run(scrape_urls_async(urls))