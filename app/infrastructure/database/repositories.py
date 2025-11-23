from __future__ import annotations
from datetime import date
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import (
    CoalPile,
    TemperatureReading,
    FireIncident,
    WeatherData,
    Prediction,
)
from app.domain.interfaces import (
    CoalPileRepository,
    TemperatureRepository,
    FireIncidentRepository,
    WeatherRepository,
    PredictionRepository,
)
from app.infrastructure.database.models import (
    Supply as SupplyModel,
    Temperature as TemperatureModel,
    Fire as FireModel,
    Weather as WeatherModel,
    Prediction as PredictionModel,
)


class SQLAlchemyCoalPileRepository(CoalPileRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, pile_id: int) -> Optional[CoalPile]:
        stmt = (
            select(SupplyModel)
            .where(SupplyModel.pile_id == pile_id)
            .order_by(SupplyModel.unloading_date.asc())
            .limit(1)
        )
        result = self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return CoalPile.model_validate(model) if model else None

    def get_all_active(self) -> List[CoalPile]:
        # Используем DISTINCT ON для PostgreSQL-совместимости
        stmt = (
            select(SupplyModel)
            .distinct(SupplyModel.pile_id)
            .order_by(SupplyModel.pile_id, SupplyModel.unloading_date.asc())
        )
        result = self.session.execute(stmt)
        models = result.scalars().all()
        return [CoalPile.model_validate(m) for m in models]

    def save(self, pile: CoalPile) -> None:
        db_obj = SupplyModel(
            unloading_date=pile.formation_date,
            coal_type=pile.coal_type,
            pile_id=pile.pile_id,
            warehouse_id=pile.warehouse_id,
            to_warehouse_ton=pile.initial_volume_tonnes,
        )
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)


class SQLAlchemyTemperatureRepository(TemperatureRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_latest_by_pile_id(self, pile_id: int) -> Optional[TemperatureReading]:
        stmt = (
            select(TemperatureModel)
            .where(TemperatureModel.pile_id == pile_id)
            .order_by(TemperatureModel.measurement_date.desc())
            .limit(1)
        )
        result = self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return TemperatureReading.model_validate(model) if model else None

    def get_by_pile_id_and_date_range(
        self, pile_id: int, start_date: date, end_date: date
    ) -> List[TemperatureReading]:
        stmt = (
            select(TemperatureModel)
            .where(
                TemperatureModel.pile_id == pile_id,
                TemperatureModel.measurement_date >= start_date,
                TemperatureModel.measurement_date <= end_date,
            )
            .order_by(TemperatureModel.measurement_date.asc())
        )
        result = self.session.execute(stmt)
        models = result.scalars().all()
        return [TemperatureReading.model_validate(m) for m in models]

    def save_batch(self, readings: List[TemperatureReading]) -> None:
        models = [
            TemperatureModel(
                measurement_date=r.measurement_date,
                warehouse_id=r.warehouse_id,
                pile_id=r.pile_id,
                coal_type=r.coal_type,
                temperature=r.temperature,
                picket=r.picket,
                shift=r.shift,
            )
            for r in readings
        ]
        self.session.add_all(models)
        self.session.commit()


class SQLAlchemyFireIncidentRepository(FireIncidentRepository):
    def __init__(
        self,
        session: Session,
        coal_pile_repo: CoalPileRepository,
    ):
        self.session = session
        self.coal_pile_repo = coal_pile_repo

    def get_by_pile_id(self, pile_id: int) -> List[FireIncident]:
        stmt = (
            select(FireModel)
            .where(FireModel.pile_id == pile_id)
            .order_by(FireModel.fire_start_date.asc())
        )
        result = self.session.execute(stmt)
        models = result.scalars().all()
        return [FireIncident.model_validate(m) for m in models]

    def get_last_fire_date_by_pile_id(self, pile_id: int) -> Optional[date]:
        stmt = (
            select(FireModel.fire_start_date)
            .where(FireModel.pile_id == pile_id)
            .order_by(FireModel.fire_start_date.desc())
            .limit(1)
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_fires_in_date_range(self, start: date, end: date) -> List[FireIncident]:
        stmt = select(FireModel).where(
            FireModel.fire_start_date >= start,
            FireModel.fire_start_date <= end,
        )
        result = self.session.execute(stmt)
        models = result.scalars().all()
        return [FireIncident.model_validate(m) for m in models]

    def save_batch(self, incidents: List[FireIncident]) -> None:
        models = []
        for inc in incidents:
            pile = self.coal_pile_repo.get_by_id(inc.pile_id)
            coal_type = pile.coal_type if pile else "UNKNOWN"
            model = FireModel(
                document_date=inc.document_date,
                coal_type=coal_type,
                pile_id=inc.pile_id,
                warehouse_id=inc.warehouse_id,
                weight_act=inc.weight_act,
                fire_start_date=inc.actual_date,
            )
            models.append(model)

        self.session.add_all(models)
        self.session.commit()


class SQLAlchemyWeatherRepository(WeatherRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_date(self, date: date) -> Optional[WeatherData]:
        stmt = select(WeatherModel).where(WeatherModel.date == date)
        result = self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return WeatherData.model_validate(model) if model else None

    def save_batch(self, weathers: List[WeatherData]) -> None:
        models = [
            WeatherModel(
                date=w.date,
                air_temperature=w.air_temperature,
                humidity=w.humidity,
            )
            for w in weathers
        ]
        self.session.add_all(models)
        self.session.commit()


class SQLAlchemyPredictionRepository(PredictionRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_pile_id_and_forecast_dates(
        self, pile_id: int, dates: List[date]
    ) -> List[Prediction]:
        stmt = select(PredictionModel).where(
            PredictionModel.pile_id == pile_id,
            PredictionModel.forecast_date.in_(dates),
        )
        result = self.session.execute(stmt)
        models = result.scalars().all()
        return [Prediction.model_validate(m) for m in models]

    def save_batch(self, predictions: List[Prediction]) -> None:
        models = [
            PredictionModel(
                warehouse_id=p.warehouse_id,
                pile_id=p.pile_id,
                prediction_date=p.prediction_date,
                forecast_date=p.forecast_date,
                risk_level=p.risk_level,
                probability=p.probability,
                model_version=p.model_version,
            )
            for p in predictions
        ]
        self.session.add_all(models)
        self.session.commit()

    def get_all_by_pile_id(self, pile_id: int) -> List[Prediction]:
        stmt = select(PredictionModel).where(PredictionModel.pile_id == pile_id)
        result = self.session.execute(stmt)
        models = result.scalars().all()
        return [Prediction.model_validate(m) for m in models]