from fastapi import FastAPI
from app.presentation.api.v1.router import router as v1_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="Coal Fire Predictor", version="0.1.0", debug=settings.debug)
    app.include_router(v1_router)
    return app


app = create_app()
