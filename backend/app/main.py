from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_tables
from app.core.scheduler import start_scheduler, stop_scheduler
from app.api.v1 import access, auth, cases, documents, issues, lawyers, legal_aid, research, chat, education, payments


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Lawgic API",
    description="AI-powered legal tech platform for India - Multi-agent legal assistance",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Browsing every resource is free — the ₹72 approval gate is enforced narrowly, only
# on the specific "give me a result" endpoints (see app/core/access.py usages in
# issues.py, documents.py, lawyers.py, research.py), not at the router level anymore.
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(access.router, prefix="/api/v1/access", tags=["Access Approval"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
app.include_router(issues.router, prefix="/api/v1/issues", tags=["Issue Navigator"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(lawyers.router, prefix="/api/v1/lawyers", tags=["Lawyers"])
app.include_router(legal_aid.router, prefix="/api/v1/legal-aid", tags=["Free Legal Aid"])
app.include_router(research.router, prefix="/api/v1/research", tags=["Research"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(education.router, prefix="/api/v1/education", tags=["Education"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])


@app.get("/")
async def root():
    return {
        "message": "Lawgic API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
