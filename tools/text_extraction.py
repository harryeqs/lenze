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
"""
def needs_js_rendering(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Heuristic check: look for indicators of dynamic content
    dynamic_indicators = [
        soup.find_all(['div', 'span'], {'class': re.compile('loading|content|dynamic|js-render')}),
        soup.find_all(attrs={"data-*": True}),
        soup.find_all('script', src=re.compile('jquery|angular|react|vue|bootstrap')),
        soup.find_all('div', text=re.compile('^\s*$')),  # Empty divs
        soup.find_all('div', {'style': re.compile('display:\s*none')})
    ]
    return any(dynamic_indicators)

# Function to fetch and render JavaScript content with Playwright
async def fetch_js_rendered_content(context, url, timeout=2):
    try:
        page = await context.new_page()
        await page.goto(url, timeout=timeout*1000, wait_until='domcontentloaded')
        content = await page.content()
        await page.close()
        return content
    except (PlaywrightError, PlaywrightTimeoutError) as e:
        print(f"PlaywrightError: Scraping {url} failed. Reason: {e}")
        return None
"""

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


if __name__ == "__main__":
    import time
    start_time = time.time()
    urls_01 = [
        "https://myjapaneseexperience.com/traditional-japanese-food/", 
        "https://www.reddit.com/r/kansascity/comments/l27sub/good_japanese-food_in_kc/", 
        "https://resobox.com/news/what-is-typical-japanese-food/", 
        "https://cooking.stackexchange.com/questions/128587/why-are-there-few-no-traditional-japanese-dishes-made-with-rice-noodles", 
        "https://www.japan-guide.com/forum/quereadisplay.html?0+77161", 
        "http://travelhungry.co/blog/2014/5/2/traditional-japanese-at-kicho", 
        "https://www.japan-guide.com/forum/quereadisplay.html?0+112743", 
        "https://www.boozefoodtravel.com/in-search-of-japanese-food-in-tokyo/", 
        "https://www.lisatselebidis.com/natto-what-it-is-why-you-should-eat-it-and-where-to-buy-it/", 
        "https://www.instagram.com/homecookingsolutions/p/C8Rg8HfPcP7/"
    ]
    urls_02 = [
        "https://www.byfood.com/blog/travel-tips/japanese-traditional-foods",
        "https://the-shooting-star.com/japan-vegan-vegetarian-survival-guide/",
        "https://www.legalnomads.com/gluten-free/japan/",
        "https://www.bbcgoodfood.com/travel/global/top-10-foods-try-japan",
        "https://www.afar.com/magazine/traditional-japanese-food",
        "https://champagneflight.com/ultimate-vegetarian-vegan-survival-guide-to-japan/",
        "https://boutiquejapan.com/food-in-fukuoka/",
        "https://www.alldayieat.com/recipe/moyashi-goma-ae-mung-bean-sprouts-sweet-sesame-soy/",
        "https://kuzefukuandsons.com/products/enoki-mushrooms-in-savory-umami-sauce",
        "https://kobesteakhouse.com/popular-japanese-food-10-mouth-watering-dishes-to-try/"
    ]
    urls_03 = [
        "https://www.uefa.com/uefachampionsleague/news/028a-1a4c5f292492-f6d3a5ee82bd-1000--2024-25-champions-league-who-has-qualified-directly-for-t/",
        "https://www.japan-guide.com/forum/quereadisplay.html?0+77161",
        "https://teaching.eng.cam.ac.uk/sites/teaching22-23.eng.cam.ac.uk/files/CUED_Newcomers_Guide%202022-2023.pdf",
        "https://arxiv.org/pdf/2304.08485"
    ]

    urls = urls_01+urls_02+urls_03
    texts = process_urls(urls)
    sources = [{'link': url, 'text': text} for url, text in zip(urls, texts)]
    print(sources)
    end_time = time.time()
    time_taken = f"Scraping took {end_time - start_time:.4f} seconds"
    print(time_taken)

