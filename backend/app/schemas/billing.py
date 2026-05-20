from pydantic import BaseModel
from datetime import datetime


class CheckoutRequest(BaseModel):
    customer_id: str
    price_id: str


class CheckoutResponse(BaseModel):
    checkout_url: str


class PlanDetailsResponse(BaseModel):
    credits: int
    price: int
    price_id: str
    description: str
    features: list


class SubscriptionDetailsResponse(BaseModel):
    id: int
    plan: str
    credits: int
    stripe_customer_id: str = None
    is_active: bool
    billing_cycle_start: datetime
    billing_cycle_end: datetime = None
    created_at: datetime
    plan_details: PlanDetailsResponse = None

    class Config:
        from_attributes = True
