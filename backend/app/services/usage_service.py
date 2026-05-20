from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.subscription import Subscription


def consume_credits(
    db: Session,
    tenant_id: int,
    amount: int
):

    subscription = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant_id)
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    if subscription.credits < amount:
        raise HTTPException(
            status_code=403,
            detail="Insufficient credits"
        )

    subscription.credits -= amount

    db.commit()

    return subscription