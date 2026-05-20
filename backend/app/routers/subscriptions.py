from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.subcription_service import upgrade_plan
from app.schemas.subscription import UpgradePlanRequest, SubscriptionResponse

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"]
)


@router.put("/upgrade/{tenant_id}", response_model=SubscriptionResponse)
def upgrade(
    tenant_id: int,
    request: UpgradePlanRequest,
    db: Session = Depends(get_db)
):
    """
    Upgrade a tenant's subscription plan.
    
    Args:
        tenant_id: The tenant ID
        request: UpgradePlanRequest with new plan name
        db: Database session
    
    Returns:
        SubscriptionResponse with updated subscription details
    
    Raises:
        HTTPException: If subscription not found or upgrade fails
    """
    try:
        subscription = upgrade_plan(
            db,
            tenant_id,
            request.plan
        )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error upgrading plan: {str(e)}"
        )