from bs4 import BeautifulSoup
import re

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')

# Standard web resource extensions to filter out from extracted email strings
INVALID_EMAIL_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js", 
    ".woff", ".woff2", ".ttf", ".eot", ".ico", ".mp4", ".mp3", "@2x", "@3x"
}

def extract_emails(soup: BeautifulSoup, domain: str = None) -> str:
    """
    Finds email addresses in the page HTML text and mailto: tags.
    Prioritizes emails matching the given domain if provided.
    """
    emails = []
    
    # 1. Search in href mailto attributes
    mailtos = soup.find_all("a", href=re.compile(r'^mailto:', re.IGNORECASE))
    for link in mailtos:
        email = link.get("href").replace("mailto:", "").replace("Mailto:", "").split("?")[0].strip()
        if email:
            emails.append(email)
            
    # 2. Extract from raw page text
    text = soup.get_text()
    emails.extend(EMAIL_REGEX.findall(text))
            
    valid_emails = []
    for email in emails:
        email = email.strip().lower()
        if any(email.endswith(ext) or (ext in email and "/" in email) for ext in INVALID_EMAIL_EXTENSIONS):
            continue
        if "example.com" in email or "yourname" in email or "username" in email:
            continue
            
        if email not in valid_emails:
            valid_emails.append(email)
            
    # 3. Prioritize emails matching the exact company domain
    if domain:
        domain_emails = [e for e in valid_emails if e.endswith(f"@{domain}")]
        if domain_emails:
            # Sort by priority keywords among domain matches
            priority_prefixes = ["info@", "contact@", "hello@", "support@", "sales@", "connect@"]
            for prefix in priority_prefixes:
                for email in domain_emails:
                    if email.startswith(prefix):
                        return email
            return domain_emails[0]
            
    # 4. Fallback to general priority keywords
    priority_prefixes = ["info@", "contact@", "hello@", "support@", "sales@", "connect@"]
    for prefix in priority_prefixes:
        for email in valid_emails:
            if email.startswith(prefix):
                return email
                
    return valid_emails[0] if valid_emails else None

def extract_social_links(soup: BeautifulSoup) -> dict:
    """
    Extracts social profile links from anchor elements.
    """
    socials = {}
    patterns = {
        "linkedin": r'linkedin\.com/(?:company|in|school|org)/[a-zA-Z0-9-_]+',
        "twitter": r'(?:twitter\.com|x\.com)/[a-zA-Z0-9-_]+',
        "facebook": r'facebook\.com/[a-zA-Z0-9-_]+',
        "instagram": r'instagram\.com/[a-zA-Z0-9-_]+',
        "youtube": r'youtube\.com/(?:c|channel|user|@)?[a-zA-Z0-9-_]+',
        "github": r'github\.com/[a-zA-Z0-9-_]+'
    }
    
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        for platform, pattern in patterns.items():
            if platform not in socials and re.search(pattern, href, re.IGNORECASE):
                if not href.startswith("http"):
                    if href.startswith("//"):
                        href = "https:" + href
                    else:
                        href = "https://" + href
                socials[platform] = href
                
    return socials
