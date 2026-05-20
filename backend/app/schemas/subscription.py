from pydantic import BaseModel


class UpgradePlanRequest(BaseModel):
    plan: str


class SubscriptionResponse(BaseModel):
    id: int
    tenant_id: int
    plan: str
    credits: int
    stripe_customer_id: str = None
    stripe_subscription_id: str = None

    class Config:
        from_attributes = True
