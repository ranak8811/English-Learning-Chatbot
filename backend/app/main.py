from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.routers.chat import router as chat_router
from app.routers.child import router as child_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes database tables on startup.
    """
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization warning: {e}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Early childhood (under 7) English learning companion with adaptive levels, child mode detection, and SEL support.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend access (Vercel, Netlify, and Localhost)
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
if not origins or "*" in origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(chat_router)
app.include_router(child_router)


@app.get("/")
def root():
    """Root welcome endpoint providing high-level system information."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "status": "online",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify backend status, routers, and configuration."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "llm_engine": settings.OPENROUTER_MODEL,
        "database": "configured (Neon Cloud PostgreSQL)",
        "routers": ["/api/chat", "/api/child"],
        "latency_budget_ms": settings.MAX_LATENCY_SLA_MS
    }
