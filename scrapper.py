import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import time
import random
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import nest_asyncio
from bs4 import BeautifulSoup
import requests
from utils.helper import _fetch_and_extract,headers
from utils.error_checking import *
from utils.email_extractor import *
# from utils.dns_checking import *
from utils.dns_checking import validate_email
from db_connection import get_db_collection


collection = get_db_collection()





# def find_emails_on_site(base_domain, paths):
#     """
#     Finds emails by concurrently iterating through common paths on a given domain
#     using a ThreadPoolExecutor.
#     """
#     all_found_emails = set()
#     base_url = f"{base_domain}/"
#     error_status = "ok"

#     print(f"Checking base URL: {base_url}")
#     try:
#         response = requests.get(base_url, headers=headers, timeout=60, allow_redirects=True)
#         error_status = get_error_status(response)
#         # print(error_status)

#         if response.status_code in [402,404]:
#           print(f"Error accessing home page {base_url}: {response.status_code } Skipping other paths for this domain.")
#           return [], error_status


#         if error_status != "ok" and response.status_code == 403:
#             print("Falling back to Playwright for base URL...")
#             emails_from_homepage, error_status_fallback = _fetch_and_extract(base_url)
#             print(f"{error_status_fallback} for Base URL {base_url} after fallback")

#             if error_status_fallback != "ok" and error_status_fallback != 200:
#                 print(f"Base URL failed even after fallback. Skipping other paths.")
#                 return emails_from_homepage, error_status_fallback

#             # Fallback succeeded, continue with other paths
#             all_found_emails.update(emails_from_homepage)
#             error_status = "ok"

#         else:
#             # If the home page is okay, extract emails directly
#             soup = BeautifulSoup(response.text, 'html.parser')
#             emails_from_homepage = extract_emails(soup.get_text(" ", strip=True))
#             all_found_emails.update(emails_from_homepage)

#     except requests.exceptions.RequestException as e:
#         print(f"Error accessing home page {base_url}: {e}. Skipping other paths for this domain.")
#         return [], error_status

#     # If home page (normal or fallback) succeeded → continue with paths
#     urls_to_check = [f"{base_domain}/{path}" for path in paths if path != ""]
#     with ThreadPoolExecutor(max_workers=5) as executor:
#         futures = {executor.submit(_fetch_and_extract, url) for url in urls_to_check}
#         for future in futures:
#             emails_from_page, error_status = future.result()
#             all_found_emails.update(emails_from_page)

#     return sorted(list(all_found_emails)), error_status



def find_emails_on_site(base_domain, paths):
    """
    Finds emails by iterating through common paths on a given domain
    using a ThreadPoolExecutor. Returns (emails, error_status).
    """
    all_found_emails = set()
    base_url = f"{base_domain}/"
    error_status = "ok"

    print(f"Checking base URL: {base_url}")
    try:
        response = requests.get(base_url, headers=headers, timeout=60, allow_redirects=True)
        error_status = get_error_status(response)

        if response.status_code in [402, 404]:
            print(f"Error accessing home page {base_url}: {response.status_code}. Skipping other paths.")
            return [], error_status

        if error_status != "ok" and response.status_code == 403:
            # Try Playwright fallback
            print("Falling back to Playwright for base URL...")
            emails_from_homepage, fb_status = _fetch_and_extract(base_url)
            print(f"{fb_status} for Base URL {base_url} after fallback")

            if fb_status != "ok" and fb_status != 200:
                # Fallback failed completely
                return emails_from_homepage, fb_status

            all_found_emails.update(emails_from_homepage)
            error_status = "ok"

        else:
            # Normal HTML parse
            soup = BeautifulSoup(response.text, 'html.parser')
            emails_from_homepage = extract_emails(soup.get_text(" ", strip=True))
            all_found_emails.update(emails_from_homepage)

    except requests.exceptions.RequestException as e:
        print(f"Error accessing home page {base_url}: {e}. Skipping other paths.")
        return [], str(e)

    # Process additional paths
    urls_to_check = [f"{base_domain}/{path}" for path in paths if path]
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(_fetch_and_extract, url) for url in urls_to_check}
        for future in futures:
            emails_from_page, path_status = future.result()
            all_found_emails.update(emails_from_page)

            # Only downgrade status if we don’t already have an error
            if error_status == "ok" and path_status != "ok":
                error_status = path_status

    return sorted(list(all_found_emails)), error_status





domains_to_check = ["https://www.adasmckinley.org","https://www.irsolutions.tech","https://www.sazzio.com","https://www.chicagoautoshow.com","https://www.sammonsfinancialgroup.com","https://www.waterna.com","https://www.colorcrushnails.com","https://www.newsweek.com"]
# domains_to_check = ['https://www.newsweek.com']
# domains_to_check = ["https://www.adasmckinley.org"]
# domains_to_check = ["https://www.fwabae.com","https://6.hosted-by.leaaseweb.oocities.org"]
# domains_to_check = ["https://www.sazzio.com","https://www.ninesol.com","https://www.majesticrobe.com/privacy-policy/"]
# domains_to_check = ['https://www.glassdoor.com.br']
# domains_to_check = ['https://www.inc.com']

# domains_to_check = [
#     #  "https://www.chicagoautoshow.com",
#      "https://www.profootballhof.com",
#     ]

# domains_to_check = df['Domain'][:20]
common_paths = [
        "", "contact", "contact-us", "contacts", "support", "help",
        "about", "about-us", "careers", "team", "reach-us","ntsa-staff", "get-in-touch","info", "customer-service", "sales", "business", "office", "locations",
        "privacy", "privacy-policy", "policies/privacy-policy",
        "pages/privacy-policies","pages/contact-us","pages/contact","pages/contacts",
        "terms", "terms-of-service", "policies/terms-of-services", "legal",
        'content/privacy-policy', 'policies/contact-information','policy/contact','policy-privacy',
        'privacy-statement','service/privacy-policy'
    ]





def domains_to_process(domains_to_check):
    """
    Process multiple domains and return a dict with raw emails,
    valid emails, and clean error status for each.
    """
    results = {}

    for domain in domains_to_check:
        raw_emails, error_status = find_emails_on_site(domain, common_paths)
        valid_emails = []

        for email in raw_emails:
            valid, _ = validate_email(email)
            if valid:
                valid_emails.append(email)

        # Decide final error status
        if error_status and error_status not in ["ok", "not_found"]:
            final_status = error_status
        elif not raw_emails and not valid_emails:
            final_status = "no emails found"
        else:
            final_status = None  # success, no error

        results[domain] = {
            "raw_emails": raw_emails,
            "valid_emails": valid_emails,
            "error_status": final_status,
        }

    return results





results = domains_to_process(domains_to_check)




for domain, data in results.items():
    print("\nDomain:", domain)
    print("Raw Emails:", data["raw_emails"])
    print("Valid Emails:", data["valid_emails"])
    print("Error Status:", data["error_status"])
    


docs = []

for domain, data in results.items():
    docs.append({
        "domain": domain,
        "raw_emails": data["raw_emails"],
        "valid_emails": data["valid_emails"],
        "error_status": data["error_status"]
    })

collection.insert_many(docs)



