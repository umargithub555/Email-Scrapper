import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import time
import random
# from dns_checking import validate_email
# from email_extractor import extract_emails
# from error_checking import get_error_status
# from utils.helper import _fetch_and_extract,headers
from utils.error_checking import *
from utils.email_extractor import *
# from utils.dns_checking import *
from utils.dns_checking import validate_email




import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import nest_asyncio
from bs4 import BeautifulSoup
import requests


nest_asyncio.apply()






REQUEST_TIMEOUT = 120
# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0 Safari/537.36"
USER_AGENT = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 OPR/94.0.0.0",
]

MAX_WORKERS_TOTAL = 30
MAX_WORKERS_PER_DOMAIN = 10
MAX_CANDIDATES = 40
# PROXIES_FILE = "/content/valid_proxies.txt"
# PROXY_ATTEMPTS = 3
# PROXY_BACKOFF_BASE = 1.5
# PROXY_JITTER = 0.3



headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": random.choice(USER_AGENT),
}





# async def fetch_with_playwright(url: str):
#     async with Stealth().use_async(async_playwright()) as p:
#         browser = await p.chromium.launch(headless=True)
#         page = await browser.new_page()

#         # browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
#         # page = await browser.new_page(ignore_https_errors=True)
#         await page.goto(url, timeout=60000)
#         html_content = await page.content()

#         # print("\n--- Stealth Status Checks ---")
#         # webdriver_status = await page.evaluate("navigator.webdriver")
#         # print("from new_page (stealth status): ", webdriver_status)

#         # different_context = await browser.new_context()
#         # page_from_different_context = await different_context.new_page()
#         # different_context_status = await page_from_different_context.evaluate("navigator.webdriver")
#         # print("from new_context (stealth status): ", different_context_status)

#         await browser.close()
#         return html_content


# async def fetch_with_playwright(url: str):
#     async with Stealth().use_async(async_playwright()) as p:
#         browser = await p.chromium.launch(headless=True)
#         page = await browser.new_page()


#         # browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
#         # page = await browser.new_page(ignore_https_errors=True)

#         # page.goto returns a Response object
#         response = await page.goto(url, timeout=60000)

#         # get status code safely
#         status = response.status if response else None
#         print(f"Status code for {url}: {status}")

#         html_content = await page.content()

#         await browser.close()
#         return html_content, status


async def fetch_with_playwright(url: str):
    status = None
    html_content = ""

    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(
            headless=True, args=["--ignore-certificate-errors"]
        )
        page = await browser.new_page(ignore_https_errors=True)

        try:
            response = await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            if response:
                status = response.status
            html_content = await page.content()
        except Exception as e:
            print(f"Playwright navigation failed for {url}: {e}")
        finally:
            await browser.close()

    return html_content, status



# async def extract_emails_with_fallback(text: str = None, url: str = None) -> list:
#     try:
#         html,status = await fetch_with_playwright(url)
#         soup = BeautifulSoup(html, "html.parser")
#         visible_text = soup.get_text(" ", strip=True)
#         # print(visible_text)
#         emails = extract_emails(visible_text)
#         return sorted(set(emails)),status
#     except Exception as e:
#         print(f"Playwright fallback failed for {url}: {e}")
#         return [],status


async def extract_emails_with_fallback(text: str = None, url: str = None) -> list:
    status = None
    try:
        html, status = await fetch_with_playwright(url)
        if not html:
            return [], status

        soup = BeautifulSoup(html, "html.parser")
        visible_text = soup.get_text(" ", strip=True)
        emails = extract_emails(visible_text)
        return sorted(set(emails)), status

    except Exception as e:
        print(f"Playwright fallback failed for {url}: {e}")
        return [], status



#  browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
#  page = await browser.new_page(ignore_https_errors=True)

def _fetch_and_extract(url:str = None,base_url:str = None):
    try:
        response = requests.get(url, headers=headers, timeout=60, allow_redirects=True)
        # print(response.text)
        error_status = get_error_status(response)
        print(error_status)
        print(response.status_code)

        # if error_status != "ok":
        #     print(f"Failed to retrieve {url}: {error_status} -- {response.status_code}")
        #     return [], error_status

        if response.status_code == 403 and (url or base_url):
            print("Access Denied/Cloudflare error --- Falling back to playwright")
            if not base_url:

              emails,status_with_fallback = asyncio.run(extract_emails_with_fallback("", url))
            else:
              emails,status_with_fallback = asyncio.run(extract_emails_with_fallback("", base_url))

            return emails, status_with_fallback

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(" ", strip=True)
        # print(page)

        text_emails = extract_emails(soup.get_text(" ", strip=True))

        if not text_emails and "[email\xa0protected]" in page_text.lower() and (url or base_url):
            print("Yes [email\xa0protected] found Falling back to playwright")
            # emails,status_with_fallback = asyncio.run(extract_emails_with_fallback("", url))
            # return emails, status_with_fallback
            if not base_url:

              emails,status_with_fallback = asyncio.run(extract_emails_with_fallback("", url))
            else:
              emails,status_with_fallback = asyncio.run(extract_emails_with_fallback("", base_url))

            return emails, status_with_fallback

        mailto_emails = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('mailto:'):
                email = href[len('mailto:'):]
                if '?' in email:
                  email = email.split('?')[0]
                mailto_emails.append(email)

        emails = list(set(text_emails + mailto_emails))
        return emails, error_status

    except requests.exceptions.SSLError as e:
        print(f"SSL error retrieving {url}: {e}")
        return [], "ssl_error"

    except Exception as e:
        print(f"General error retrieving {url}: {e}")
        return [], "error"

