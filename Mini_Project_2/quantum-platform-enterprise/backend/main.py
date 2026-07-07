from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config.settings import settings
from core.middleware.logging_middleware import EnterpriseLoggingMiddleware
from core.middleware.security import SecurityHeadersMiddleware
from core.exceptions.base import BaseAPIException
from core.logging.json_logger import setup_logging
from api.v1.endpoints import auth, users, experiments, analytics
from analytics.events.subscribers import setup_analytics_subscriptions

setup_logging()
setup_analytics_subscriptions()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version=settings.VERSION
)

app.add_middleware(EnterpriseLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(BaseAPIException)
async def custom_api_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.detail},
    )

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(experiments.router, prefix=f"{settings.API_V1_STR}/experiments", tags=["Experiments"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics"])
app.add_route("/metrics", analytics.metrics)

@app.get("/health", tags=["Infrastructure"])
def health_check():
    return {"status": "ok", "version": settings.VERSION}
    
@app.get("/system/status", tags=["Infrastructure"])
def system_status():
    return {"status": "operational", "quantum_engine": "standby", "database": "connected"}