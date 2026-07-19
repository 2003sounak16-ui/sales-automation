from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from database.crud import get_lead, update_lead, add_event

from services.email.smtp_client import send_outreach_email_via_smtp, _build_html_email

router = APIRouter(prefix="/api")

class SendEmailRequest(BaseModel):
    lead_id: str

class PreviewEmailRequest(BaseModel):
    subject: str
    body: str

@router.post("/preview-email")
def preview_email(payload: PreviewEmailRequest):
    """
    Returns the fully rendered HTML email body without sending anything.
    Used by the frontend Email Preview Modal.
    """
    try:
        html = _build_html_email(
            subject=payload.subject or "Email Preview",
            body_text=payload.body or ""
        )
        return {"html": html}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to render email preview: {str(e)}"
        )

@router.post("/send")
def send_outreach_email(payload: SendEmailRequest):
    """
    Sends the outreach email to the prospect using Resend service client.
    """
    try:
        lead = get_lead(payload.lead_id)
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead with ID {payload.lead_id} not found."
            )
            
        # Dispatch outreach email
        result = send_outreach_email_via_smtp(
            to_email=lead.get("contact_email"),
            subject=lead.get("ai_subject"),
            body_text=lead.get("ai_body")
        )
        
        # Update lead status to SENT
        updated = update_lead(payload.lead_id, {
            "status": "SENT"
        })
        
        # Log timeline event
        add_event(payload.lead_id, "EMAIL_SENT", {
            "recipient": lead.get("contact_email") or "owner@example.com",
            "subject": lead.get("ai_subject"),
            "resend_id": result.get("id"),
            "delivery_status": result.get("status")
        })
        
        return {
            "status": "success",
            "message": f"Email outreach dispatched successfully to {lead.get('contact_email') or 'owner@example.com'}",
            "resend_id": result.get("id"),
            "lead": updated
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )

