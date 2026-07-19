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
