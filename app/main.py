
from fastapi import FastAPI

from app.api.routes import customers, products, sales
from app.config.settings import settings


app = FastAPI(
    title=settings.app_name,
    description="Business management API with AI integration planned.",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "application": settings.app_name,
        "environment": settings.app_env,
    }


app.include_router(products.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(sales.router, prefix="/api/v1")