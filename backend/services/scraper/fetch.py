import httpx
import urllib3
from utils.retry import retry
from utils.exceptions import ScraperError

# Suppress insecure request warnings due to verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

@retry(exceptions=(httpx.HTTPError, httpx.RequestError), tries=3, delay=1.0)
def fetch_html(url: str, timeout: int = 10) -> tuple:
    """
    Fetches the HTML page content of a given URL.
    Returns a tuple of (html_text, final_url) where final_url reflects
    the actual URL after following any redirects.
    """
    try:
        # Follow redirects, use verify=False to bypass SSL errors on self-signed/expired domains
        with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=timeout, verify=False) as client:
            response = client.get(url)
            response.raise_for_status()
            final_url = str(response.url)
            return response.text, final_url
    except Exception as e:
        print(f"Scraper fetch error for URL '{url}': {e}")
        raise ScraperError(f"Failed to fetch content from URL '{url}': {e}") from e

