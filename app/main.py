from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.presentation.api.v1.router import router as v1_router


def create_app() -> FastAPI:
    app = FastAPI(title="Coal Fire Predictor", version="0.1.0", debug=settings.debug)

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React
            "http://localhost:8501",  # Streamlit
            "http://localhost:5174",  # Vite (ваш текущий фронтенд)
            # разрешить все локальные порты:
            # "http://localhost:*",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(v1_router)
    return app


app = create_app()
