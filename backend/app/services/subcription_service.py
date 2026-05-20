from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.core.config import PLAN_LIMITS


def upgrade_plan(
    db: Session,
    tenant_id: int,
    new_plan: str
):
    """
    Upgrade a tenant's subscription plan.
    
    Args:
        db: Database session
        tenant_id: The tenant ID
        new_plan: The new plan name
    
    Returns:
        Updated Subscription object
    
    Raises:
        ValueError: If subscription not found or plan is invalid
    """
    subscription = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant_id)
        .first()
    )

    if not subscription:
        raise ValueError(f"Subscription not found for tenant {tenant_id}")

    if new_plan not in PLAN_LIMITS:
        raise ValueError(f"Invalid plan: {new_plan}")

    subscription.plan = new_plan
    subscription.credits = PLAN_LIMITS[new_plan]["credits"]

    db.commit()
    db.refresh(subscription)

    return subscription