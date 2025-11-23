from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, Index
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Supply(Base):
    __tablename__ = "supplies"
    __table_args__ = (
        Index("idx_supplies_composite", "warehouse_id", "pile_id", "unloading_date"),
    )

    supply_id = Column(Integer, primary_key=True, index=True)
    unloading_date = Column(Date, nullable=False)
    coal_type = Column(String(50), nullable=False)
    pile_id = Column(Integer, nullable=False)
    warehouse_id = Column(Integer, nullable=False)
    loading_ship_date = Column(Date)
    to_warehouse_ton = Column(Numeric(15, 4), nullable=False)
    to_ship_ton = Column(Numeric(15, 4))
    loaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Fire(Base):
    __tablename__ = "fires"
    __table_args__ = (
        Index("idx_fires_composite", "warehouse_id", "pile_id", "fire_start_date"),
    )

    fire_id = Column(Integer, primary_key=True, index=True)
    document_date = Column(Date, nullable=False)
    coal_type = Column(String(10), nullable=False)
    pile_id = Column(Integer, nullable=False)
    warehouse_id = Column(Integer, nullable=False)
    weight_act = Column(Numeric(10, 2), nullable=False)
    fire_start_date = Column(Date, nullable=False)
    fire_end_date = Column(Date)
    pile_formation_start = Column(Date)
    loaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Temperature(Base):
    __tablename__ = "temperatures"
    __table_args__ = (
        Index("idx_temperatures_composite", "warehouse_id", "pile_id", "measurement_date"),
        Index("idx_temperatures_temp", "temperature"),
    )

    temperature_id = Column(Integer, primary_key=True, index=True)
    measurement_date = Column(Date, nullable=False)
    warehouse_id = Column(Integer, nullable=False)
    pile_id = Column(Integer, nullable=False)
    coal_type = Column(String(50), nullable=False)
    temperature = Column(Numeric(5, 2), nullable=False)
    picket = Column(String(50))
    shift = Column(Integer)
    loaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Weather(Base):
    __tablename__ = "weather"
    __table_args__ = (
        Index("idx_weather_date", "date"),
    )

    weather_id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True)
    air_temperature = Column(Numeric(5, 2), nullable=False)
    temp_min = Column(Numeric(5, 2))
    temp_max = Column(Numeric(5, 2))
    humidity = Column(Numeric(5, 2), nullable=False)
    pressure = Column(Integer)
    wind_speed_avg = Column(Numeric(5, 2))
    wind_speed_max = Column(Numeric(5, 2))
    precipitation = Column(Numeric(5, 2))
    weather_condition = Column(String(100))
    loaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Prediction(Base):
    __tablename__ = "predictions"
    __table_args__ = (
        Index("idx_predictions_composite", "warehouse_id", "pile_id", "prediction_date", "forecast_date"),
    )

    prediction_id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, nullable=False)
    pile_id = Column(Integer, nullable=False)
    prediction_date = Column(Date, nullable=False)
    forecast_date = Column(Date, nullable=False)
    risk_level = Column(String(10), nullable=False)
    probability = Column(Numeric(5, 4), nullable=False)
    model_version = Column(String(20), default="v1.0")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))