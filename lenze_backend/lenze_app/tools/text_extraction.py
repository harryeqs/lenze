import asyncio
import aiohttp
import fitz
from playwright.async_api import async_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
from readability import Document
from bs4 import BeautifulSoup
import re

# Function to fetch webpage content asynchronously with aiohttp
async def fetch_webpage(session, url, timeout=3):
    try:
        async with session.get(url, timeout=timeout) as response:
            content_type = response.headers.get('content-type')
            if content_type and 'application/pdf' in content_type:
                pdf_buffer = await response.read()
                #print(f'URL: {url}, Type: PDF')
                return pdf_buffer, 'pdf'
            elif content_type and 'text/html' in content_type:
                content = await response.text()
                #print(f'URL: {url}, Type: HTML')
                return content, 'html'
            else:
                return None, 'error'
    except Exception as e:
        print(f"FetchError: Scraping {url} failed. Reason: {e}")
        return None, 'error'

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_buffer, max_content=5000):
    pdf_document = fitz.open(stream=pdf_buffer, filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text[:max_content]

# Function to clean extracted text
def clean_text(text):
    text = re.sub(r'\n\s*\n', '\n', text)  # Remove empty lines
    text = re.sub(r'(?i)Acknowledgements.*?\n', '', text, flags=re.DOTALL)  # Remove acknowledgements section
    text = re.sub(r'(?i)References.*?\n', '', text, flags=re.DOTALL)  # Remove references section
    text = re.sub(r'(?i)Navigation.*?\n', '', text, flags=re.DOTALL)  # Remove navigation sections
    return text.strip()

# Function to extract main content from HTML
def extract_main_content(html):
    if html:
        doc = Document(html)
        return doc.summary()
    else:
        return None

# Function to convert HTML content to plain text
def extract_plain_text(html_content, max_content=5000):
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Remove elements you consider irrelevant
        for irrelevant in soup(['header', 'footer', 'nav', 'aside']):
            irrelevant.decompose()
        return soup.get_text(separator='\n', strip=True)[:max_content]
    else:
        return 'Error fetching content'

async def process_url(session, url):
    content, content_type = await fetch_webpage(session, url)
    if content_type == 'pdf':
        text = extract_text_from_pdf(content)
    elif content_type == 'html':
        main_content_html = extract_main_content(content)
        text = clean_text(extract_plain_text(main_content_html))
    else:
        text = "Error fetching content."
    return text

# Function to process a list of URLs concurrently with a semaphore
async def process_urls_async(urls, concurrency=10):
    """
    async with aiohttp.ClientSession() as session:
        async with async_playwright() as p:
            # browser = await p.chromium.launch(headless=True)
            # context = await browser.new_context()
            semaphore = asyncio.Semaphore(max_concurrent_tasks)
            
            async def sem_task(url):
                async with semaphore:
                    return await process_url(session, url)
            
            tasks = [sem_task(url) for url in urls]
            results = await asyncio.gather(*tasks)
            # await browser.close()
            return results
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def scrape_with_sem(url):
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                return await process_url(session, url)

    tasks = [scrape_with_sem(url) for url in urls]
    return await asyncio.gather(*tasks)

def process_urls(urls):
    return asyncio.run(process_urls_async(urls))

