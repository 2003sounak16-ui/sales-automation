"""
Email Generator
===============
Generates personalised B2B outreach emails using Groq's LLM API.
Falls back to a polished mock template when Groq is unavailable.
"""
from services.ai.groq_client import get_groq_client
from services.ai.prompts import SYSTEM_PROMPT, format_user_prompt
from services.ai.validator import clean_and_parse_json
from utils.retry import retry
from utils.exceptions import AIError

# Use the largest available Groq model for best writing quality.
# llama-3.3-70b-versatile produces noticeably better sales copy than 8b.
DEFAULT_MODEL = "llama-3.3-70b-versatile"

# Professional sign-off appended after the AI body
SIGN_OFF = "Best,\nAlex Rivera | SalesFlow AI"


@retry(exceptions=(Exception,), tries=3, delay=1.0)
def _call_groq_api(client, system_prompt: str, user_prompt: str):
    """Executes the chat completion call to Groq with retry logic."""
    return client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.65,          # Slightly creative but consistent
        max_tokens=512,
        response_format={"type": "json_object"},
    )


def generate_outreach_email(
    company_name: str,
    industry: str = None,
    description: str = None,
    about_text: str = None,
    website: str = None,
) -> dict:
    """
    Generate a personalized B2B outreach email for the prospect.

    Args:
        company_name: Target company name.
        industry:     Industry sector (optional; AI will infer if blank).
        description:  Meta description scraped from company homepage.
        about_text:   About / mission text scraped from company homepage.
        website:      Company homepage URL for context.

    Returns:
        dict with keys: subject, body, industry, country
    """
    client = get_groq_client()

    if client:
        try:
            user_prompt = format_user_prompt(
                company_name=company_name,
                industry=industry,
                description=description,
                about_text=about_text,
                website=website or "",
            )

            completion = _call_groq_api(client, SYSTEM_PROMPT, user_prompt)
            raw = completion.choices[0].message.content
            result = clean_and_parse_json(raw)

            # Append professional sign-off to the AI-generated body
            if result.get("body"):
                result["body"] = result["body"].rstrip() + f"\n\n{SIGN_OFF}"

            return result

        except Exception as exc:
            print(f"Groq API call failed: {exc}")
            raise AIError(f"Groq AI generation failed: {exc}") from exc

    # Polished mock fallback when client is not configured
    return get_mock_email(company_name, industry, website)


def get_mock_email(
    company_name: str,
    industry: str = None,
    website: str = None,
) -> dict:
    """
    High-quality mock email for local testing without a Groq API key.
    Follows the same 3-paragraph structure enforced by the system prompt.
    """
    ind = industry or "Technology"
    site_ref = f" at {website}" if website else ""

    subject = f"Scaling outbound for {company_name}"
    body = (
        f"I came across {company_name}{site_ref} recently and was genuinely "
        f"impressed by the focus you are bringing to the {ind} space — "
        f"the kind of product thinking that stands out.\n\n"

        f"I lead growth at SalesFlow AI, a platform that automates the full "
        f"outbound prospecting cycle: company discovery, AI-generated outreach "
        f"drafts, a reviewer approval queue, and one-click Resend dispatch. "
        f"Teams like yours typically cut 10+ hours of weekly SDR research "
        f"and double pipeline velocity within the first 30 days.\n\n"

        f"Would you have 15 minutes this week to see how it fits your workflow?\n\n"
        f"{SIGN_OFF}"
    )
    return {
        "subject": subject,
        "body": body,
        "industry": ind,
        "country": "Global",
    }
