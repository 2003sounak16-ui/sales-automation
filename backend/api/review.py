from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from database.crud import get_pending_reviews, update_lead, add_event

router = APIRouter(prefix="/api")

class ApproveLeadRequest(BaseModel):
    lead_id: str
    ai_subject: str
    ai_body: str

@router.get("/pending")
def list_pending():
    """
    Retrieves all leads pending human review.
    """
    try:
        pending = get_pending_reviews()
        return pending
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pending reviews: {str(e)}"
        )

@router.post("/approve")
def approve_lead(payload: ApproveLeadRequest):
    """
    Saves edited outreach content and transitions the lead status to APPROVED.
    """
    try:
        updated = update_lead(payload.lead_id, {
            "ai_subject": payload.ai_subject,
            "ai_body": payload.ai_body,
            "status": "APPROVED"
        })
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead with ID {payload.lead_id} not found."
            )
        
        # Log approval event
        add_event(payload.lead_id, "REVIEW_APPROVED", {
            "subject": payload.ai_subject
        })
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve lead: {str(e)}"
        )
