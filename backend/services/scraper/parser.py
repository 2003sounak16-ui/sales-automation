from bs4 import BeautifulSoup
from services.scraper.fetch import fetch_html
from services.scraper.metadata import extract_title, extract_description, extract_about_text
from services.scraper.contact import extract_emails, extract_social_links
from urllib.parse import urlparse, urljoin

# Subpages commonly containing contact information
CONTACT_SUBPAGES = ["/contact", "/contact-us", "/about", "/about-us", "/impressum", "/team"]


def _domains_match(original_domain: str, final_domain: str) -> bool:
    """
    Check whether the final (redirected) domain is meaningfully the same
    as the original. Handles www stripping and subdomain tolerance.
    e.g. www.sutrixa.com == sutrixa.com → True
         sutrixa.com vs http.dev        → False
    """
    original_domain = original_domain.lower().replace("www.", "")
    final_domain = final_domain.lower().replace("www.", "")
    return original_domain == final_domain or final_domain.endswith("." + original_domain)


def scrape_website(url: str) -> dict:
    """
    Fetches and parses a target website URL to extract company profiles.
    Also probes common subpages (/contact, /about) for email addresses
    if none are found on the homepage.

    Redirect-aware: if the URL redirects to a completely different domain,
    the scraper will reject emails from the foreign domain and attempt
    subpage crawling on the ORIGINAL domain instead.

    Returns contact_email=None when no verifiable email exists on the site.
    """
    if not url:
        return _empty_profile("unknown.com")

    try:
        parsed_url = urlparse(url)
        original_domain = parsed_url.netloc.replace("www.", "")
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Fetch with redirect tracking
        html, final_url = fetch_html(url)
        final_parsed = urlparse(final_url)
        final_domain = final_parsed.netloc.replace("www.", "")

        # Detect if the page redirected to a completely different domain
        redirected_to_foreign = not _domains_match(original_domain, final_domain)

        if redirected_to_foreign:
            print(
                f"[Scraper] Redirect detected: {url} → {final_url} "
                f"(original domain '{original_domain}' ≠ final domain '{final_domain}'). "
                f"Emails from '{final_domain}' will be ignored."
            )

        soup = BeautifulSoup(html, "html.parser")

        title = extract_title(soup)
        desc = extract_description(soup)
        about = extract_about_text(soup)

        # --- Email extraction: homepage first, only if domain matches ---
        email = None
        if not redirected_to_foreign:
            email = extract_emails(soup, original_domain)

        # --- If no email on homepage, probe common subpages on the ORIGINAL domain ---
        if not email:
            for subpage in CONTACT_SUBPAGES:
                try:
                    sub_url = urljoin(base_url, subpage)
                    sub_html, sub_final_url = fetch_html(sub_url)

                    # Check this subpage also stays on the same domain
                    sub_final_domain = urlparse(sub_final_url).netloc.replace("www.", "")
                    if not _domains_match(original_domain, sub_final_domain):
                        continue  # Subpage also redirects away, skip

                    sub_soup = BeautifulSoup(sub_html, "html.parser")
                    email = extract_emails(sub_soup, original_domain)
                    if email:
                        # Also grab about text from subpage if main page had none
                        if not about or about == desc:
                            sub_about = extract_about_text(sub_soup)
                            if sub_about and len(sub_about) > len(about or ""):
                                about = sub_about
                        break
                except Exception:
                    continue  # Subpage doesn't exist or timed out; move on

        socials = extract_social_links(soup)

        if not title:
            title = original_domain.split(".")[0].capitalize()
        if not desc:
            desc = f"Official website of {title}."
        if not about:
            about = desc

        return {
            "title": title,
            "description": desc,
            "about_text": about,
            "contact_email": email,  # None if nothing found — never fabricated
            "social_links": socials
        }
    except Exception as e:
        print(f"Scraping failed for '{url}': {e}. Returning empty profile.")
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace("www.", "") or "unknown.com"
        except Exception:
            domain = "unknown.com"
        return _empty_profile(domain)


def _empty_profile(domain: str) -> dict:
    """
    Returns a structured profile with no fabricated data.
    """
    company_name = domain.split(".")[0].capitalize()
    return {
        "title": f"{company_name}",
        "description": f"Could not retrieve information from {domain}.",
        "about_text": "",
        "contact_email": None,
        "social_links": {}
    }
