import os
from dotenv import load_dotenv

load_dotenv()

# Security
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Token Expiry
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
)

PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "30")
)

# Rate Limiting
RATE_LIMIT_REQUESTS = int(
    os.getenv("RATE_LIMIT_REQUESTS", "120")
)

RATE_LIMIT_WINDOW_SECONDS = int(
    os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")
)

# Database
DEFAULT_DATABASE_URL = (
    "postgresql://postgres:Bala%401612@localhost/enterprisecollab"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DEFAULT_DATABASE_URL
)

# Redis
REDIS_URL = os.getenv("REDIS_URL")

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

VITE_STRIPE_PUBLISHABLE_KEY = os.getenv(
    "VITE_STRIPE_PUBLISHABLE_KEY"
)

STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")

# Plan Limits
PLAN_LIMITS = {
    "Basic": {
        "credits": 100,
        "price": 0,
        "price_id": os.getenv("STRIPE_BASIC_PRICE_ID"),
        "description": "Perfect for getting started",
        "features": [
            "100 Credits/month",
            "Basic Analytics",
            "Community Support",
            "1 Team Member"
        ]
    },

    "Silver": {
        "credits": 1000,
        "price": 999,
        "price_id": os.getenv("STRIPE_SILVER_PRICE_ID"),
        "description": "For growing teams",
        "features": [
            "1000 Credits/month",
            "Advanced Analytics",
            "Email Support",
            "Up to 5 Team Members",
            "Custom Branding"
        ]
    },

    "Gold": {
        "credits": 10000,
        "price": 4999,
        "price_id": os.getenv("STRIPE_GOLD_PRICE_ID"),
        "description": "For enterprise needs",
        "features": [
            "10000 Credits/month",
            "Full Analytics Suite",
            "24/7 Priority Support",
            "Unlimited Team Members",
            "Custom Integrations",
            "SLA Guarantee"
        ]
    }
}