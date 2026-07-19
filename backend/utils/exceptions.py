class SalesAutomationError(Exception):
    """Base exception class for all errors in the sales automation system."""
    pass


class ScraperError(SalesAutomationError):
    """Raised when website scraping or HTML fetching fails after retries."""
    pass


class AIError(SalesAutomationError):
    """Raised when the AI generation API fails or yields invalid output after retries."""
    pass


class EmailDeliveryError(SalesAutomationError):
    """Raised when Resend email dispatch fails after retries."""
    pass


class EnrichmentError(SalesAutomationError):
    """Raised when contact enrichment or Hunter.io API fails."""
    pass
