import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = None
is_configured = False

if GROQ_API_KEY and "your-" not in GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        is_configured = True
        print("Groq Client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")
else:
    print("GROQ_API_KEY is not configured or uses placeholder. Using mock generator fallback.")

def get_groq_client() -> Groq:
    """
    Returns the initialized Groq client, or None if not configured.
    """
    return client if is_configured else None
