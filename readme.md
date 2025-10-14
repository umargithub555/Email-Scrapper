# 📧 Email Extraction & Validation Tool

A powerful Python-based email extraction and validation tool designed for **company lead generation**.  
The script crawls domains and their **30+ subdomains**, extracts email addresses using **BeautifulSoup**, **Regex**, and **Playwright** (for protected or JS-rendered pages), and finally **validates each email** using **DNS + SMTP checks**.

---

## 🚀 Features

✅ **Multi-subdomain scanning** – Automatically checks 30+ common subdomains (`www`, `mail`, `support`, `info`, `blog`, etc.)  
✅ **Email extraction** – Uses `requests`, `BeautifulSoup`, and `regex` to extract valid emails from HTML and text content  
✅ **Fallback with Playwright** – Handles 403 or bot-protected pages and extracts dynamically rendered emails  
✅ **Email validation** – Verifies emails via DNS MX lookup and SMTP handshake before adding to the final list  
✅ **Custom headers and delays** – Prevents blocking and detection during scraping  
✅ **Clean output** – Saves extracted and validated emails in structured format (CSV/JSON) or mongodb.

---

## 🧠 How It Works

1. **Fetch Pages**

   - Uses `requests` to fetch each subdomain page of the target domain.
   - If access is denied (`403`) or content is JS-rendered, it switches to **Playwright** for browser-based extraction.

2. **Extract Emails**

   - Parses HTML with `BeautifulSoup`.
   - Uses **regular expressions** to detect and clean email patterns.

3. **Validate Emails**

   - Performs **DNS MX record lookup** to verify the domain’s mail server.
   - Conducts **SMTP handshake** to confirm deliverability.

4. **Save Results**
   - Stores results in `emails.csv` or `emails.json` with `status` and `source URL`.

---

## 🛠️ Tech Stack

- **Python 3.x**
- [`requests`](https://pypi.org/project/requests/) — for HTTP requests
- [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/) — for HTML parsing
- [`re`](https://docs.python.org/3/library/re.html) — for regex-based email extraction
- [`playwright`](https://playwright.dev/python/) — for JavaScript-rendered or protected pages
- [`dnspython`](https://pypi.org/project/dnspython/) — for DNS MX record lookup
- [`smtplib`](https://docs.python.org/3/library/smtplib.html) — for SMTP verification

---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/email-extraction.git
cd email-extraction

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

## Usage

```bash
python scrapper.py
```

Before using please take a look at mongodb connection string in .env.example for storing emails in mongodb.
