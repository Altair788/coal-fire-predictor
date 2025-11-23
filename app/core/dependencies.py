from typing import Generator
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.domain.interfaces import (
    CoalPileRepository,
    TemperatureRepository,
    FireIncidentRepository,
    WeatherRepository,
    PredictionRepository,
    MLService,
)
from app.infrastructure.database.repositories import (
    SQLAlchemyCoalPileRepository,
    SQLAlchemyTemperatureRepository,
    SQLAlchemyFireIncidentRepository,
    SQLAlchemyWeatherRepository,
    SQLAlchemyPredictionRepository,
)
from app.infrastructure.ml.adapter import MLModelAdapter


# Настройка движка и сессии SQLAlchemy
engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """Фабрика сессии БД для FastAPI Depends."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_coal_pile_repository(session: Session = Depends(get_db_session)) -> CoalPileRepository:
    return SQLAlchemyCoalPileRepository(session)


def get_temperature_repository(session: Session = Depends(get_db_session)) -> TemperatureRepository:
    return SQLAlchemyTemperatureRepository(session)


def get_fire_incident_repository(
    session: Session = Depends(get_db_session),
    pile_repo: CoalPileRepository = Depends(get_coal_pile_repository),
) -> FireIncidentRepository:
    return SQLAlchemyFireIncidentRepository(session, pile_repo)


def get_weather_repository(session: Session = Depends(get_db_session)) -> WeatherRepository:
    return SQLAlchemyWeatherRepository(session)


def get_prediction_repository(session: Session = Depends(get_db_session)) -> PredictionRepository:
    return SQLAlchemyPredictionRepository(session)


def get_ml_service() -> MLService:
    return MLModelAdapter()