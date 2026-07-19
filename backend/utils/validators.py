import re
from urllib.parse import urlparse

# Standard email validation regex conforming to RFC 5322
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)


def validate_url(url: str) -> bool:
    """
    Validates if the given string is a correctly formatted HTTP/HTTPS URL.
    """
    if not url:
        return False
    try:
        parsed = urlparse(url)
        # Must have scheme (http or https) and netloc (domain)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """
    Validates if the given string matches the standard email syntax.
    """
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email))
