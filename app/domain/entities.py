from datetime import date
from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict, Field


class CoalPile(BaseModel):
    """
    Статическая информация о штабеле угля.
    Источник: supplies.csv → колонка 'Наим. ЕТСНГ', 'ВыгрузкаНаСклад', 'На склад, тн'
    """
    model_config = ConfigDict(from_attributes=True)

    pile_id: int
    coal_type: str
    formation_date: date  # Дата первой выгрузки на склад
    initial_volume_tonnes: float  # Начальный объём (суммарный или по первой поставке)
    warehouse_id: int


class TemperatureReading(BaseModel):
    """
    Замер температуры в штабеле.
    Источник: temperature.csv
    """
    model_config = ConfigDict(from_attributes=True)

    pile_id: int
    warehouse_id: int
    measurement_date: date
    temperature: float
    picket: Optional[str] = None
    shift: Optional[int] = None


class FireIncident(BaseModel):
    """
    Подтверждённый факт самовозгорания.
    Источник: fires.csv
    """
    model_config = ConfigDict(from_attributes=True)

    pile_id: int
    warehouse_id: int
    actual_date: date  # Дата возгорания
    document_date: date  # Дата составления акта
    weight_act: float


class WeatherData(BaseModel):
    """
    Агрегированные погодные данные за день.
    Источник: weather.csv → агрегация по дням
    """
    model_config = ConfigDict(from_attributes=True)

    date: date
    air_temperature: float  # Средняя температура воздуха
    humidity: float  # Средняя влажность (%)
    # Остальные поля (wind, pressure и т.д.) не используются в модели


class RiskForecast(BaseModel):
    """
    Прогноз риска на 3 дня вперёд.
    Соответствует Приложению B контракта с дата-сайентистом.
    """

    pile_id: int
    forecast_date: date  # Дата, на которую сделан прогноз (обычно = measurement_date)
    risk_levels: Dict[str, str] = Field(
        ..., description='{"day_1": "low", "day_2": "medium", "day_3": "high"}'
    )
    probabilities: Dict[str, float] = Field(
        ..., description='{"day_1": 0.12, "day_2": 0.45, "day_3": 0.81}'
    )


class Prediction(BaseModel):
    """
    Единая запись прогноза для хранения в БД (для одного дня из прогноза на 3 дня).
    Используется в таблице `predictions`.
    """

    model_config = ConfigDict(from_attributes=True)

    pile_id: int
    warehouse_id: int
    prediction_date: date  # Когда был сделан прогноз
    forecast_date: date  # На какую дату прогноз
    risk_level: str  # "low", "medium", "high"
    probability: float
    model_version: str = "v1.0"
