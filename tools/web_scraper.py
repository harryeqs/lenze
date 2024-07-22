import aiohttp
import asyncio
from bs4 import BeautifulSoup
from io import BytesIO
import fitz
import time
from playwright.async_api import async_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
from typing import List

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

async def fetch_content(session, url: str, timeout: float = 1) -> str:
    """
    Fetches content from a URL using aiohttp.
    """
    try:
        async with session.get(url, timeout=timeout, headers=HEADERS) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"ClientError: Failed to fetch {url}, status code: {response.status}")
                return ""
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"ClientError: Unable to access URL: {url}. Reason: {e}")
        return ""

async def scrape_html_content(session, url: str, max_content: int = 5000) -> str:
    """
    Scrapes text content from an HTML page using aiohttp and BeautifulSoup.
    """
    html_content = await fetch_content(session, url)
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "lxml")
    main_content = soup.find('main') or soup.find('article') or soup.body

    text = ""
    if main_content:
        title = soup.find('title').get_text() if soup.find('title') else ""
        paragraphs = main_content.find_all('p')
        text = title + '\n' + '\n'.join(p.get_text() for p in paragraphs)
    return text[:max_content]

async def scrape_pdf_async(url: str, timeout: float = 2, max_content: int = 5000) -> str:
    """
    Scrapes text content from a PDF page asynchronously.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(f"Failed to fetch {url}, status code: {response.status}")
                if response.headers.get('Content-Type') != 'application/pdf':
                    raise ValueError("The URL does not point to a PDF file.")
                
                remote_file = await response.read()
                memory_file = BytesIO(remote_file)
                pdf_document = fitz.open(stream=memory_file, filetype='pdf')

                text = ""
                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    text += page.get_text()

                return text[:max_content]
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"ClientError: Unable to access URL: {url}. Reason: {e}.")
        return ""

async def scrape_js_rendered_page(url: str, timeout: float = 1.5, max_content: int = 5000) -> str:
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

            soup = BeautifulSoup(content, 'lxml')
            main_content = soup.find('main') or soup.find('article') or soup.body

            text = ""
            if main_content:
                title = soup.find('title').get_text() if soup.find('title') else ""
                paragraphs = main_content.find_all('p')
                text = title + '\n' + '\n'.join(p.get_text() for p in paragraphs)
            return text[:max_content]
    except (PlaywrightError, PlaywrightTimeoutError) as e:
        print(f"PlaywrightError: Scraping {url} failed. Reason: {e}")
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
                content = await scrape_html_content(session, url)
                if content:
                    return content
            except Exception as e:
                print(f"Exception: Unable to access URL: {url} using aiohttp. Exception: {e}")

        print(f"Falling back to Playwright for JavaScript-rendered page: {url}")
        return await scrape_js_rendered_page(url)

async def scrape_urls_async(urls: List[str], concurrency: int = 10) -> List[str]:
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
    """
    return asyncio.run(scrape_urls_async(urls, concurrency))

if __name__ == "__main__":
    start_time = time.time()
    urls_01 = [
        "https://myjapaneseexperience.com/traditional-japanese-food/", 
        "https://www.reddit.com/r/kansascity/comments/l27sub/good_japanese_food_in_kc/", 
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
        "https://www.uefa.com/uefachampionsleague/fixtures-results/#/d/2024-07-17",
        "https://www.japan-guide.com/forum/quereadisplay.html?0+77161",
        "https://olympics.com/en/sports/", 
        "https://arxiv.org/pdf/2304.08485"
    ]
    scraped_texts = scrape_urls(urls_03)
    end_time = time.time()
    print(scraped_texts[0])
    time_taken = f"Scraping took {end_time - start_time:.4f} seconds"
    print(time_taken)