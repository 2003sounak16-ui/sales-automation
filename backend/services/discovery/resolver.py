from urllib.parse import urlparse
import re

EXCLUDED_DOMAINS = {
    "wikipedia.org",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "crunchbase.com",
    "github.com",
    "glassdoor.com",
    "medium.com",
    "bloomberg.com",
    "forbes.com",
    "ycombinator.com",
    "techcrunch.com",
    "reddit.com",
    "pinterest.com",
    "tripadvisor.com",
    "quora.com",
    "indeed.com",
    "zoominfo.com",
    "upwork.com",
    "fiverr.com"
}

def is_social_or_directory(url: str) -> bool:
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        
        # Check against exclusions
        for excluded in EXCLUDED_DOMAINS:
            if domain == excluded or domain.endswith("." + excluded):
                return True
        return False
    except Exception:
        return True

def clean_company_name(name: str) -> str:
    # Lowercase and remove common corporate suffixes and non-alphanumeric chars
    name = name.lower().strip()
    name = re.sub(r'\b(inc|ltd|co|corp|corporation|llc|gmbh|solutions|technologies|group)\b\.?', '', name)
    name = re.sub(r'[^a-z0-9]', '', name)
    return name

def resolve_official_website(company_name: str, search_results: list) -> str:
    """
    Ranks and filters search results to find the company's official website.
    search_results is a list of dicts, e.g. [{"title": ..., "link": ..., "snippet": ...}]
    """
    if not search_results:
        return None

    cleaned_company = clean_company_name(company_name)
    candidates = []
    
    for i, res in enumerate(search_results):
        url = res.get("link") or res.get("href")
        if not url or not url.startswith("http"):
            continue
            
        if is_social_or_directory(url):
            continue

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace("www.", "")
            domain_part = domain.split(".")[0]
            
            score = 0
            
            # Domain matches company name
            if cleaned_company in domain_part or domain_part in cleaned_company:
                score += 10
            
            # Exact domain match
            if domain_part == cleaned_company:
                score += 15

            # Position in search results (earlier is better)
            position_penalty = i * 2
            score -= position_penalty

            candidates.append((url, score))
        except Exception:
            continue

    if not candidates:
        # Fallback to the first non-social link
        for res in search_results:
            url = res.get("link") or res.get("href")
            if url and url.startswith("http") and not is_social_or_directory(url):
                return url
        return None

    # Sort candidates by score descending
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]
