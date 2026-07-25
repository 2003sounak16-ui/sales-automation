import os
from dotenv import load_dotenv
from groq import Groq

_cached_client = None
_cached_key = None

def get_groq_client() -> Groq:
    """
    Returns an initialized Groq client if a valid API key is present in environment,
    or None if not configured / placeholder.
    Dynamically re-loads environment variables so API key edits take effect without server restart.
    """
    global _cached_client, _cached_key

    # Reload .env to pick up any key updates dynamically
    load_dotenv(override=True)

    api_key = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")

    # Check for empty key or placeholder strings
    if (
        not api_key
        or "your_" in api_key.lower()
        or "your-" in api_key.lower()
        or "placeholder" in api_key.lower()
    ):
        _cached_client = None
        _cached_key = None
        return None

    # If key hasn't changed and client exists, reuse it
    if _cached_client is not None and _cached_key == api_key:
        return _cached_client

    try:
        client = Groq(api_key=api_key)
        _cached_client = client
        _cached_key = api_key
        print("Groq Client initialized successfully.")
        return _cached_client
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")
        _cached_client = None
        _cached_key = None
        return None

