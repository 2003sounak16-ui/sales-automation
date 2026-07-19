from fastapi import APIRouter, HTTPException, status
from database.crud import get_all_leads

router = APIRouter(prefix="/api")

@router.get("/leads")
def list_leads():
    """
    Returns all leads in the system.
    """
    try:
        leads = get_all_leads()
        return leads
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch leads: {str(e)}"
        )
