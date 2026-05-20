from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from datetime import datetime

from app.db.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), unique=True)

    # Plan: Basic, Silver, Gold
    plan = Column(String, default="Basic", index=True)
    credits = Column(Integer, default=100)
    
    # Stripe information
    stripe_customer_id = Column(String, nullable=True, unique=True, index=True)
    stripe_subscription_id = Column(String, nullable=True, unique=True, index=True)
    
    # Billing cycle
    billing_cycle_start = Column(DateTime, default=datetime.utcnow)
    billing_cycle_end = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)