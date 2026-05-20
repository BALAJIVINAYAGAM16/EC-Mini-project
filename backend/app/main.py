import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.db.schema_sync import ensure_schema
from app.core.rate_limit import rate_limit_middleware
from app.models import (  # Import all models to register them with SQLAlchemy
    Tenant,
    User,
    Task,
    Approval,
    ApprovalHistory,
    Comment,
    Document,
    Notification,
    ActivityLog,
    AuditLog,
    Subscription,
)
from app.routers import (
    activity,
    approval,
    auth,
    comments,
    dashboard,
    kanban,
    task,
    users,
    document,
    audit,
    notification,
    websocket,
    billing,
    organization,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("mini_enterprise")

app = FastAPI(title="Mini Enterprise Collaboration Workflow")

# DATABASE
Base.metadata.create_all(bind=engine)
ensure_schema(engine)

# CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(auth.router)
app.include_router(task.router)
app.include_router(users.router)
app.include_router(kanban.router)
app.include_router(comments.router)
app.include_router(approval.router)
app.include_router(dashboard.router)
app.include_router(activity.router)
app.include_router(document.router)
app.include_router(audit.router)
app.include_router(notification.router)
app.include_router(websocket.router)
app.include_router(billing.router)
app.include_router(organization.router)

# RATE LIMIT
@app.middleware("http")
async def rate_limit_requests(request, call_next):
    return await rate_limit_middleware(request, call_next)

# LOGGING
@app.middleware("http")
async def log_requests(request, call_next):
    started_at = time.perf_counter()

    response = await call_next(request)

    duration_ms = (time.perf_counter() - started_at) * 1000

    logger.info(
        "%s %s -> %s %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response