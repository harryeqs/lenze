import asyncio
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from asyncio import Semaphore
import re
import aiohttp

async def fetch_pdf(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    pdf_buffer = await response.read()
                    return pdf_buffer
                else:
                    return f"Failed to fetch PDF: HTTP Status {response.status}"
    except Exception as e:
        return f"Error fetching PDF: {str(e)}"

def extract_text_from_pdf(pdf_buffer, max_content=5000):
    try:
        # Open the PDF using bytes
        pdf_document = fitz.open(stream=pdf_buffer, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        return text[:max_content]
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def clean_text(text):
    try:
        text = re.sub(r'\n\s*\n', '\n', text)  # Remove empty lines
        text = re.sub(r'(?i)Acknowledgements.*?\n', '', text, flags=re.DOTALL)  # Remove acknowledgements section
        text = re.sub(r'(?i)References.*?\n', '', text, flags=re.DOTALL)  # Remove references section
        text = re.sub(r'(?i)Navigation.*?\n', '', text, flags=re.DOTALL)  # Remove navigation sections
        return text.strip()
    except Exception as e:
        return f"Error cleaning text: {str(e)}"

def extract_main_content(html, max_content=3000):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        for element in soup(['nav', 'header', 'footer', 'aside', 'form', 'script', 'noscript', 'style', 'meta', 'link']):
            element.extract()
        for class_name in ['sidebar', 'nav', 'footer', 'advertisement', 'acknowledgement', 'comment', 'comments']:
            for element in soup.find_all(class_=class_name):
                element.extract()
        for id_name in ['sidebar', 'nav', 'footer', 'advertisement', 'acknowledgement', 'comment', 'comments']:
            for element in soup.find_all(id=id_name):
                element.extract()
        text = soup.get_text(separator='\n', strip=True)
        return text[:max_content]
    except Exception as e:
        return f"Error extracting main content from HTML: {str(e)}"

async def process_url(url, context, semaphore, retries=1, timeout=10):
    async with semaphore:
        try:
            page = await context.new_page()
        except Exception as e:
            return f"Failed to open a new page for {url}: {str(e)}"

        for attempt in range(retries):
            try:
                return await asyncio.wait_for(
                    process_url_inner(url, page),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                await page.close()
                return f"Timeout reached for {url} after {timeout} seconds"
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(0.5)
                else:
                    await page.close()
                    return f"Failed to fetch {url} after {retries} attempts: {str(e)}"

async def process_url_inner(url, page):
    # Check if the URL ends with .pdf or contains /pdf/ in the path
    if url.lower().endswith('.pdf') or '/pdf/' in url.lower():
        try:
            # Close the page as we'll fetch the PDF directly using aiohttp
            await page.close()
            pdf_buffer = await fetch_pdf(url)
            if isinstance(pdf_buffer, str):  # Check if there was an error fetching the PDF
                return pdf_buffer
            pdf_text = extract_text_from_pdf(pdf_buffer)
            return pdf_text
        except Exception as e:
            return f"Error processing PDF at {url}: {str(e)}"

    # If it's not a PDF, proceed with HTML content processing
    await page.goto(url, wait_until='domcontentloaded')
    try:
        content = await page.content()
        cleaned_content = clean_text(extract_main_content(content))
        await page.close()
        return cleaned_content
    except Exception as e:
        await page.close()
        return f"Error processing HTML content at {url}: {str(e)}"

async def process_urls_async(urls, concurrency=10, timeout=10):
    semaphore = Semaphore(concurrency)
    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        except Exception as e:
            return [f"Failed to launch browser or create context: {str(e)}"]

        tasks = [process_url(url, context, semaphore, timeout=timeout) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        await context.close()
        await browser.close()

        return results

if __name__ == "__main__":
    import time
    urls = [
        'https://www.imdb.com/list/ls033398199/',
        'https://www.imdb.com/list/ls064849128/',
        'https://community.openai.com/t/can-linkreader-plugin-be-used-with-the-openai-api/281902/13',
        'https://arxiv.org/pdf/2407.20183',
        'https://gptstore.ai/plugins/-gochitchat-ai',
        'https://www.uefa.com/about/what-we-do/our-values/',
        'https://www.tripadvisor.co.uk/TravelersChoice-ThingsToDo',
        'https://www.formula1.com/en/latest/all'
    ]
    start_time = time.time()
    content_list = asyncio.run(process_urls_async(urls))
    end_time = time.time()
    for i, content in enumerate(content_list):
        print(f"Content from URL {urls[i]}:\n")
        print(content)
        print("\n" + "="*80 + "\n")
    print(f'Time taken: {end_time-start_time:.4f}s')
