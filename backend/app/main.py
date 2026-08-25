from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.access import require_approved_access
from app.core.config import settings
from app.core.database import create_tables
from app.api.v1 import access, auth, cases, documents, issues, lawyers, research, chat, education, payments


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


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

# Auth and the access-request flow itself must stay reachable by a *pending* user —
# every other router requires approved access (or admin), enforced once here rather
# than per-endpoint. chat.router is the one exception: its websocket route does its
# own token-query-param auth (no Authorization header to hang a dependency off), so
# its gate is applied inline in chat.py instead.
_gated = [Depends(require_approved_access)]

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(access.router, prefix="/api/v1/access", tags=["Access Approval"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"], dependencies=_gated)
app.include_router(issues.router, prefix="/api/v1/issues", tags=["Issue Navigator"], dependencies=_gated)
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"], dependencies=_gated)
app.include_router(lawyers.router, prefix="/api/v1/lawyers", tags=["Lawyers"], dependencies=_gated)
app.include_router(research.router, prefix="/api/v1/research", tags=["Research"], dependencies=_gated)
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(education.router, prefix="/api/v1/education", tags=["Education"], dependencies=_gated)
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"], dependencies=_gated)


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
