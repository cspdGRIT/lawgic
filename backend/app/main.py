from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_tables
from app.api.v1 import auth, cases, documents, lawyers, research, chat, education, payments


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

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(lawyers.router, prefix="/api/v1/lawyers", tags=["Lawyers"])
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
