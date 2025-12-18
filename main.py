"""
BMB - Bite Me Buddy
Main FastAPI application with all routes and functionality
"""

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import logging
import os
import time
from datetime import datetime
import asyncio

from database import engine, Base, get_db
from core.config import settings
from core.exceptions import BaseCustomException, AuthenticationError, AuthorizationError
from core.logging import setup_logging
from routers import auth, customer, team_member, admin, orders, services, uploads
from utils.twilio_client import init_twilio
from utils.clock_utils import get_ist_time

# Setup logging
logger = setup_logging()

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting BMB - Bite Me Buddy application...")
    
    # Initialize database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize Twilio client
    init_twilio()
    
    logger.info("Application started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title="BMB - Bite Me Buddy",
    description="Food Ordering Platform with Admin Panel",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Templates
templates = Jinja2Templates(directory="templates")

# Global exception handlers
@app.exception_handler(BaseCustomException)
async def custom_exception_handler(request: Request, exc: BaseCustomException):
    """Handle custom exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code}
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    if request.headers.get("HX-Request"):
        return HTMLResponse("<div class='alert alert-danger'>Page not found</div>", status_code=404)
    return templates.TemplateResponse("errors/404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    if request.headers.get("HX-Request"):
        return HTMLResponse("<div class='alert alert-danger'>Internal server error</div>", status_code=500)
    return templates.TemplateResponse("errors/500.html", {"request": request}, status_code=500)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} - {request.client.host}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.2f}s")
    
    return response

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers"""
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(customer.router, prefix="/api/customer", tags=["customer"])
app.include_router(team_member.router, prefix="/api/team", tags=["team"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(services.router, prefix="/api/services", tags=["services"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with clock and navigation buttons"""
    current_time = get_ist_time()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_time": current_time
    })

# Health check endpoint
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "timestamp": get_ist_time().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )

# Admin login page (accessible via secret clock)
@app.get("/admin-login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin/login.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )