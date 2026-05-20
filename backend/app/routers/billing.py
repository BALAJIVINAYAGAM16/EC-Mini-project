from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import stripe
from datetime import datetime, timedelta

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.subcription import Subscription
from app.services.billing_service import create_checkout_session
from app.schemas.billing import CheckoutResponse, SubscriptionDetailsResponse
from app.core.config import STRIPE_SECRET_KEY, PLAN_LIMITS

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)


@router.get("/plans")
def get_available_plans():
    """
    Get all available subscription plans with pricing and features.
    
    Returns:
        List of available plans with details
    """
    plans = []
    for plan_name, plan_details in PLAN_LIMITS.items():
        plans.append({
            "name": plan_name,
            "price": plan_details["price"],
            "credits": plan_details["credits"],
            "description": plan_details["description"],
            "features": plan_details["features"]
        })
    return plans


@router.get("/subscription", response_model=SubscriptionDetailsResponse)
def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current subscription details for the authenticated user's tenant.
    
    Returns:
        SubscriptionDetailsResponse with subscription info and plan details
    
    Raises:
        HTTPException: If user has no tenant or subscription not found
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=400,
            detail="User is not associated with a tenant"
        )
    
    subscription = db.query(Subscription).filter(
        Subscription.tenant_id == current_user.tenant_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )
    
    plan_details = PLAN_LIMITS.get(subscription.plan, {})
    
    return {
        "id": subscription.id,
        "plan": subscription.plan,
        "credits": subscription.credits,
        "stripe_customer_id": subscription.stripe_customer_id,
        "is_active": subscription.is_active,
        "billing_cycle_start": subscription.billing_cycle_start,
        "billing_cycle_end": subscription.billing_cycle_end,
        "created_at": subscription.created_at,
        "plan_details": plan_details
    }


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe checkout session for upgrading subscription.
    
    Returns:
        CheckoutResponse with checkout_url
    
    Raises:
        HTTPException: If user has no tenant, subscription not found, or Stripe errors
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=400,
            detail="User is not associated with a tenant. Please contact support."
        )
    
    subscription = db.query(Subscription).filter(
        Subscription.tenant_id == current_user.tenant_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail=f"No subscription found for tenant {current_user.tenant_id}. Please contact support."
        )
    
    if not subscription.stripe_customer_id:
        raise HTTPException(
            status_code=400,
            detail="Subscription not linked to Stripe. Please contact support."
        )
    
    try:
        stripe.Customer.retrieve(subscription.stripe_customer_id)
    except stripe.error.InvalidRequestError:
        raise HTTPException(
            status_code=400,
            detail=f"Customer {subscription.stripe_customer_id} not found in Stripe"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validating customer: {str(e)}"
        )
    
    try:
        plan_details = PLAN_LIMITS.get(subscription.plan, {})
        price_id = plan_details.get("price_id")
        
        if not price_id:
            raise ValueError(f"No price ID configured for plan {subscription.plan}")
        
        session = create_checkout_session(
            customer_id=subscription.stripe_customer_id,
            price_id=price_id
        )

        return {
            "checkout_url": session.url
        }
    except stripe.error.InvalidRequestError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Stripe request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating checkout session: {str(e)}"
        )


@router.post("/upgrade/{plan_name}")
def upgrade_plan(
    plan_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade subscription to a new plan immediately (for Basic/Free tier).
    For paid plans, use /billing/checkout instead.
    
    Args:
        plan_name: Target plan name (Basic, Silver, Gold)
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated subscription details
    
    Raises:
        HTTPException: If plan invalid, user has no tenant, or upgrade fails
    """
    if plan_name not in PLAN_LIMITS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid plan. Available plans: {list(PLAN_LIMITS.keys())}"
        )
    
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=400,
            detail="User is not associated with a tenant"
        )
    
    subscription = db.query(Subscription).filter(
        Subscription.tenant_id == current_user.tenant_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )
    
    try:
        plan_details = PLAN_LIMITS[plan_name]
        subscription.plan = plan_name
        subscription.credits = plan_details["credits"]
        subscription.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(subscription)
        
        return {
            "plan": subscription.plan,
            "credits": subscription.credits,
            "message": f"Successfully upgraded to {plan_name} plan"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error upgrading plan: {str(e)}"
        )