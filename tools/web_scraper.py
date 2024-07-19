from bs4 import BeautifulSoup
import fitz
from io import BytesIO
import asyncio
import aiohttp
import time
from typing import List
from playwright.async_api import async_playwright, Error as PlaywrightError

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

async def fetch_content(session, url: str, timeout: int = 3) -> str:
    """
    Fetches content from a URL using aiohttp.
    """
    try:
        async with session.get(url, timeout=timeout, headers=HEADERS) as response:
            if response.status != 200:
                raise aiohttp.ClientError(f"Failed to fetch {url}, status code: {response.status}")
            content = await response.text()
            return content
    except (aiohttp.ClientError or asyncio.TimeoutError) as e:
        print(f"ClientError: Unable to access URL: {url}. Reason: {e}")
        return ""

async def scrape_html_content(session, url: str, max_content: int = 5000) -> str:
    """
    Scrapes text content from an HTML page using aiohttp and BeautifulSoup.
    """
    html_content = await fetch_content(session, url)
    if not html_content:
        return ""

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

async def scrape_pdf_async(url: str, timeout: int = 3, max_content: int = 5000) -> str:
    """
    Scrapes text content from a PDF page asynchronously.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(f"Failed to fetch {url}, status code: {response.status}")
                content_type = response.headers.get('Content-Type')
                if content_type != 'application/pdf':
                    raise ValueError("The URL does not point to a PDF file.")
                
                remote_file = await response.read()
                memory_file = BytesIO(remote_file)
                pdf_document = fitz.open(stream=memory_file, filetype='pdf')

                text = ""
                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    text += page.get_text()

                return text[:max_content]
    except (aiohttp.ClientError or asyncio.TimeoutError) as e:
        print(f"ClientError: Unable to access URL: {url}. Reason: {e}.") 

    return ""

async def scrape_js_rendered_page(url: str, timeout: int = 3, max_content: int = 5000) -> str:
    """
    Scrapes text content from a JavaScript-rendered page using Playwright.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=timeout*1000)
            await page.wait_for_selector("body", timeout=timeout*1000)

            content = await page.content()
            await browser.close()

            soup = BeautifulSoup(content, 'html.parser')
            main_content = soup.find('main') or soup.find('article') or soup.body

            text = ""
            if main_content:
                title = soup.find('title').get_text() if soup.find('title') else ""
                paragraphs = main_content.find_all('p')
                text = title
                for paragraph in paragraphs:
                    text += '\n' + paragraph.get_text()
            return text[:max_content]
    except PlaywrightError:
        print(f"TimeoutError: Scraping {url} took longer than {timeout} seconds.")
        return ""

async def scrape_url_async(url: str) -> str:
    """
    Scrapes text content from a single URL asynchronously.
    """
    if url.lower().endswith('.pdf') or ('/pdf/' in url):
        return await scrape_pdf_async(url)
    else:
        async with aiohttp.ClientSession() as session:
            try:
                return await scrape_html_content(session, url)
            except Exception as e:
                print(f"Exception: Unable to access URL: {url}. Exception: {e}")
                print("Falling back to Playwright for JavaScript-rendered page.")
                return await scrape_js_rendered_page(url)
    return ""

async def scrape_urls_async(urls: List[str], concurrency: int = 5) -> List[str]:
    """
    Scrapes text content from a list of URLs asynchronously with limited concurrency.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def scrape_with_sem(url):
        async with semaphore:
            return await scrape_url_async(url)

    tasks = [scrape_with_sem(url) for url in urls]
    return await asyncio.gather(*tasks)

def scrape_urls(urls: List[str], concurrency: int = 10) -> List[str]:
    """
    Wrapper function to run the async scraper with limited concurrency.

    :param urls: List of URLs to scrape text from.
    :type urls: List[str]
    :param concurrency: Number of concurrency to run.
    :type concurrency: int (optional)
    :return: A list of scraped texts.
    :rtype: List[str]
    """
    return asyncio.run(scrape_urls_async(urls, concurrency))

