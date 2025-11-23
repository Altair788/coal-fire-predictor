from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from app.domain.entities import (
    CoalPile,
    TemperatureReading,
    FireIncident,
    WeatherData,
    RiskForecast,
    Prediction,
)


class CoalPileRepository(ABC):
    @abstractmethod
    def get_by_id(self, pile_id: int) -> Optional[CoalPile]:
        pass

    @abstractmethod
    def get_all_active(self) -> List[CoalPile]:
        pass

    @abstractmethod
    def save(self, pile: CoalPile) -> None:
        pass


class TemperatureRepository(ABC):
    @abstractmethod
    def get_latest_by_pile_id(self, pile_id: int) -> Optional[TemperatureReading]:
        pass

    @abstractmethod
    def get_by_pile_id_and_date_range(
        self, pile_id: int, start_date: date, end_date: date
    ) -> List[TemperatureReading]:
        pass

    @abstractmethod
    def save_batch(self, readings: List[TemperatureReading]) -> None:
        pass


class FireIncidentRepository(ABC):
    @abstractmethod
    def get_by_pile_id(self, pile_id: int) -> List[FireIncident]:
        pass

    @abstractmethod
    def get_last_fire_date_by_pile_id(self, pile_id: int) -> Optional[date]:
        pass

    @abstractmethod
    def get_fires_in_date_range(self, start: date, end: date) -> List[FireIncident]:
        pass

    @abstractmethod
    def save_batch(self, incidents: List[FireIncident]) -> None:
        pass


class WeatherRepository(ABC):
    @abstractmethod
    def get_by_date(self, date: date) -> Optional[WeatherData]:
        pass

    @abstractmethod
    def save_batch(self, weathers: List[WeatherData]) -> None:
        pass


class PredictionRepository(ABC):
    @abstractmethod
    def get_by_pile_id_and_forecast_dates(
        self, pile_id: int, dates: List[date]
    ) -> List[Prediction]:
        pass

    @abstractmethod
    def save_batch(self, predictions: List[Prediction]) -> None:
        pass


class MLService(ABC):
    @abstractmethod
    def predict_risk(self, pile_features: dict) -> dict:
        """
        Вызывает ML-модель.
        Возвращает словарь в формате из Приложения B контракта с дата-сайентистом.
        """
        pass