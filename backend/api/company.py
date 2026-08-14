from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from database.crud import get_lead_events
from orchestrator.workflow import run_analysis_pipeline

router = APIRouter(prefix="/api")

class CompanyAnalyzeRequest(BaseModel):
    website_url: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None

@router.post("/company/analyze", status_code=status.HTTP_201_CREATED)
def analyze_company(payload: CompanyAnalyzeRequest):
    """
    Triggers the analysis pipeline for a company name or website.
    """
    try:
        if not payload.company_name:
            import urllib.parse
            domain = urllib.parse.urlparse(payload.website_url).netloc or payload.website_url
            domain = domain.replace('www.', '')
            payload.company_name = domain.split('.')[0].capitalize()

        lead = run_analysis_pipeline(
            company_name=payload.company_name,
            website_url=payload.website_url,
            industry=payload.industry,
            country=payload.country
        )
        return lead
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline failed: {str(e)}"
        )

@router.get("/timeline/recent")
def get_recent_timeline_events():
    """
    Retrieves the 10 most recent lead events across all leads.
    """
    try:
        from database.connection import get_db
        db = get_db()
        response = db.table("lead_events").select("*, leads(company_name)").order("created_at", desc=True).limit(50).execute()
        return response.data if response.data else []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch recent timeline events: {str(e)}"
        )

@router.get("/timeline/{lead_id}")
def get_timeline(lead_id: str):
    """
    Retrieves all audit events for a given lead.
    """
    events = get_lead_events(lead_id)
    return events

@router.get("/companies/trending")
def get_trending_companies():
    """
    Retrieves high-growth trending companies across key industries with market signals.
    """
    return [
        {
            "id": "tr-1",
            "company_name": "Supabase",
            "website_url": "https://supabase.com",
            "industry": "Developer Tools / Database",
            "country": "United States",
            "growth_rate": "+68% YoY",
            "intent_score": "High Intent",
            "employee_count": "150-250",
            "signals": ["Recent Series B extension", "Rapid API adoption in Enterprise", "Hiring 15+ backend engineers"],
            "description": "Open source Firebase alternative providing Postgres database, Authentication, Instant APIs, Realtime subscriptions, and Storage."
        },
        {
            "id": "tr-2",
            "company_name": "Vercel",
            "website_url": "https://vercel.com",
            "industry": "Cloud Platform & Frontend",
            "country": "United States",
            "growth_rate": "+54% YoY",
            "intent_score": "High Intent",
            "employee_count": "500-1000",
            "signals": ["AI SDK v4 release", "Expanding Enterprise sales team", "High outbound email conversion rate"],
            "description": "Frontend cloud platform enabling developer teams to iterate quickly and build high-performance web applications."
        },
        {
            "id": "tr-3",
            "company_name": "Resend",
            "website_url": "https://resend.com",
            "industry": "Transactional Email Infrastructure",
            "country": "United States",
            "growth_rate": "+120% YoY",
            "intent_score": "High Intent",
            "employee_count": "20-50",
            "signals": ["Series A funding announced", "Viral developer adoption", "Expanding APAC enterprise team"],
            "description": "Modern email API built for developers, providing deliverability insights and React email templates."
        },
        {
            "id": "tr-4",
            "company_name": "Linear",
            "website_url": "https://linear.app",
            "industry": "Project Management / SaaS",
            "country": "United States",
            "growth_rate": "+45% YoY",
            "intent_score": "Moderate Intent",
            "employee_count": "50-100",
            "signals": ["Linear Asks launched", "Scaling B2B sales team", "High NPS among tech startups"],
            "description": "Issue tracking tool designed for high-performance product teams to streamline software development."
        },
        {
            "id": "tr-5",
            "company_name": "Pinecone",
            "website_url": "https://pinecone.io",
            "industry": "Vector DB / AI Infrastructure",
            "country": "United States",
            "growth_rate": "+92% YoY",
            "intent_score": "High Intent",
            "employee_count": "100-200",
            "signals": ["Serverless Vector Search launched", "Expanding LLM partner ecosystem", "High enterprise search demand"],
            "description": "Vector database that empowers developers to build fast, accurate, and scalable GenAI applications."
        },
        {
            "id": "tr-6",
            "company_name": "PostHog",
            "website_url": "https://posthog.com",
            "industry": "Product Analytics & AI",
            "country": "United States",
            "growth_rate": "+75% YoY",
            "intent_score": "High Intent",
            "employee_count": "50-150",
            "signals": ["Open-source LLM analytics module", "Profitable growth trajectory", "Active B2B buyer intent"],
            "description": "All-in-one developer-focused product analytics, session replay, feature flags, and A/B testing suite."
        }
    ]

