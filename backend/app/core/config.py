import os


SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
DEFAULT_DATABASE_URL = "postgresql://postgres:Bala%401612@localhost/enterprisecollab"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
