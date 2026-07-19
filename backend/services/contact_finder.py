import logging
from database.crud import get_lead, add_event

logger = logging.getLogger(__name__)

async def enrich_lead(lead_id: str) -> dict:
    """Enrich a lead with a verified contact email.
    Hunter API is removed as per user request.
    """
    lead = get_lead(lead_id)
    if not lead:
        raise ValueError(f"Lead with ID {lead_id} not found")
    
    add_event(lead_id, "CONTACT_ENRICH_SKIP", {"reason": "enrichment disabled"})
    return lead
