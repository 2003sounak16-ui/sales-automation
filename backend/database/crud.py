from database.connection import get_db

def create_lead(company_name: str, industry: str = None, country: str = None, status: str = "DISCOVERY_PENDING") -> dict:
    """
    Creates a new lead in the leads table.
    """
    db = get_db()
    data = {
        "company_name": company_name,
        "industry": industry,
        "country": country,
        "status": status
    }
    response = db.table("leads").insert(data).execute()
    return response.data[0] if response.data else None

def update_lead(lead_id: str, data: dict) -> dict:
    """
    Updates an existing lead with new properties.
    """
    db = get_db()
    response = db.table("leads").update(data).eq("id", lead_id).execute()
    return response.data[0] if response.data else None

def get_lead(lead_id: str) -> dict:
    """
    Retrieves details of a single lead by its ID.
    """
    db = get_db()
    response = db.table("leads").select("*").eq("id", lead_id).execute()
    return response.data[0] if response.data else None

def get_pending_reviews() -> list:
    """
    Retrieves all leads with a PENDING_REVIEW status.
    """
    db = get_db()
    response = db.table("leads").select("*").eq("status", "PENDING_REVIEW").execute()
    return response.data if response.data else []

def add_event(lead_id: str, event_type: str, details: dict = None) -> dict:
    """
    Creates an audit event inside the lead_events table for tracking workflow history.
    """
    db = get_db()
    data = {
        "lead_id": lead_id,
        "event_type": event_type,
        "details": details or {}
    }
    response = db.table("lead_events").insert(data).execute()
    return response.data[0] if response.data else None

def get_all_leads() -> list:
    """
    Retrieves all leads from the leads table.
    """
    db = get_db()
    response = db.table("leads").select("*").execute()
    return response.data if response.data else []

def get_lead_events(lead_id: str) -> list:
    """
    Retrieves all events associated with a lead, sorted by created_at.
    """
    db = get_db()
    response = db.table("lead_events").select("*").eq("lead_id", lead_id).execute()
    data = response.data if response.data else []
    try:
        data.sort(key=lambda x: x.get("created_at", ""))
    except Exception:
        pass
    return data
