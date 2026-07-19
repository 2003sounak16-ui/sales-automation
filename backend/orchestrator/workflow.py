import asyncio
import sys
import traceback

# Reconfigure stdout/stderr to use UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from database.crud import create_lead, update_lead, add_event, get_lead
from services.scraper.parser import scrape_website
from services.ai.email_generator import generate_outreach_email
from services.contact_finder import enrich_lead


def run_analysis_pipeline(company_name: str, industry: str = None, country: str = None, website_url: str = None) -> dict:
    """
    Coordinates the entire lead analysis pipeline:
    Company Name → Discovery → Scraper → (optional) Contact Enrichment → AI Generation → Pending Review.
    Logs timeline events at each stage.
    """
    # 1. Initialize the Lead in the database
    lead = create_lead(
        company_name=company_name,
        industry=industry,
        country=country,
        status="DISCOVERY_PENDING",
    )
    if not lead:
        raise ValueError(f"Failed to create database lead record for '{company_name}'")
    lead_id = lead["id"]
    add_event(lead_id, "DISCOVERY_PENDING", {"company_name": company_name})

    try:
        # 2. Phase 1
        if not website_url:
            raise ValueError("Website URL is required to fetch data.")
            
        print(f"[{company_name}] Phase 1: Using provided URL '{website_url}'...")
        lead = update_lead(lead_id, {"website": website_url, "status": "SCRAPING_PENDING"})
        add_event(lead_id, "DISCOVERY_SUCCESS", {"website": website_url})

        # 3. Website Scraper
        print(f"[{company_name}] Phase 2: Scraping '{website_url}'...")
        scraped_data = scrape_website(website_url)
        
        # Determine email availability — never crash if absent
        contact_email = scraped_data.get("contact_email")
        email_status = "found" if contact_email else "not_detected"
        
        if not contact_email:
            print(f"[{company_name}] No verifiable email detected on {website_url}. Lead will proceed without contact email.")

        lead = update_lead(lead_id, {
            "description": scraped_data["description"],
            "about_text": scraped_data["about_text"],
            "contact_email": contact_email,
            "social_links": scraped_data["social_links"],
            "status": "AI_PENDING",
        })
        add_event(lead_id, "SCRAPER_SUCCESS", {
            "title": scraped_data["title"],
            "contact_email": contact_email,
            "email_status": email_status,
            "social_links": scraped_data["social_links"],
        })

        # 4. Optional Contact Enrichment via Hunter.io
        try:
            lead = asyncio.run(enrich_lead(lead_id))
        except Exception as e:
            print(f"[{company_name}] Contact enrichment error: {e}")
            # Continue processing; email may still be missing

        # 5. Groq AI Email Generation
        print(f"[{company_name}] Phase 3: Generating personalized outreach email...")
        ai_email = generate_outreach_email(
            company_name=company_name,
            industry=industry,
            description=scraped_data["description"],
            about_text=scraped_data["about_text"],
            website=website_url,
        )
        inferred_industry = ai_email.get("industry") or industry
        inferred_country = ai_email.get("country") or country
        lead = update_lead(lead_id, {
            "ai_subject": ai_email.get("subject"),
            "ai_body": ai_email.get("body"),
            "industry": inferred_industry,
            "country": inferred_country,
            "status": "PENDING_REVIEW",
        })
        add_event(lead_id, "AI_GENERATED", {
            "subject": ai_email.get("subject"),
            "industry": inferred_industry,
            "country": inferred_country,
        })
        print(f"[{company_name}] Pipeline completed successfully. Status set to PENDING_REVIEW.")
        return lead
    except Exception as e:
        print(f"[{company_name}] Pipeline error encountered: {e}")
        trace = traceback.format_exc()
        # Transition lead state to FAILED
        update_lead(lead_id, {"status": "FAILED"})
        add_event(lead_id, "FAILED", {"error": str(e), "traceback": trace})
        raise e
