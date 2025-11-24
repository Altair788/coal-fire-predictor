from datetime import date, timedelta
from typing import List

from app.domain.entities import RiskForecast, Prediction, CoalPile
from app.domain.interfaces import (
    CoalPileRepository,
    TemperatureRepository,
    FireIncidentRepository,
    WeatherRepository,
    PredictionRepository,
    MLService,
)


class CalculateFireRisk:
    """
    Use Case для расчёта прогноза риска самовозгорания.
    Выполняет сбор признаков, вызов ML-модели и сохранение прогнозов.
    """

    def __init__(
        self,
        pile_repo: CoalPileRepository,
        temp_repo: TemperatureRepository,
        fire_repo: FireIncidentRepository,
        weather_repo: WeatherRepository,
        prediction_repo: PredictionRepository,
        ml_service: MLService,
    ):
        self.pile_repo = pile_repo
        self.temp_repo = temp_repo
        self.fire_repo = fire_repo
        self.weather_repo = weather_repo
        self.prediction_repo = prediction_repo
        self.ml_service = ml_service

    def execute(self, forecast_date: date = None) -> List[RiskForecast]:
        if forecast_date is None:
            # Получаем последнюю дату замера температуры среди всех штабелей
            piles = self.pile_repo.get_all_active()
            if not piles:
                raise ValueError("Нет активных штабелей")
            latest_dates = []
            for pile in piles:
                temp = self.temp_repo.get_latest_by_pile_id(pile.pile_id)
                if temp:
                    latest_dates.append(temp.measurement_date)
            if not latest_dates:
                raise ValueError("Нет данных о температуре — невозможно сделать прогноз")
            forecast_date = max(latest_dates)  # самая свежая дата из всех штабелей

        piles = self.pile_repo.get_all_active()
        forecasts = []

        for pile in piles:
            features = self._build_pile_features(pile, forecast_date)
            if not features:
                continue

            try:
                ml_result = self.ml_service.predict_risk(features)
            except Exception:
                continue

            predictions = self._convert_to_predictions(ml_result, pile.warehouse_id, forecast_date)
            self.prediction_repo.save_batch(predictions)

            risk_forecast = RiskForecast(
                pile_id=ml_result["pile_id"],
                forecast_date=forecast_date,
                risk_levels=ml_result["risk_levels"],
                probabilities=ml_result["probabilities"],
            )
            forecasts.append(risk_forecast)

        return forecasts

    def _build_pile_features(self, pile: CoalPile, forecast_date: date) -> dict | None:
        """Собирает признаки в формате Приложения A контракта с дата-сайентистом."""
        # Дни в хранилище
        days_in_storage = (forecast_date - pile.formation_date).days

        # Последняя температура
        latest_temp = self.temp_repo.get_latest_by_pile_id(pile.pile_id)
        if not latest_temp:
            return None

        # Температурные признаки за 7 дней
        start_7d = forecast_date - timedelta(days=7)
        temps_7d = self.temp_repo.get_by_pile_id_and_date_range(
            pile.pile_id, start_7d, forecast_date
        )
        if len(temps_7d) < 2:
            temp_trend_7d = 0.0
        else:
            # Упрощённый расчёт тренда через разницу последней и первой
            temp_trend_7d = float(temps_7d[-1].temperature - temps_7d[0].temperature)

        temp_avg_7d = sum(t.temperature for t in temps_7d) / len(temps_7d) if temps_7d else latest_temp.temperature
        temp_max_7d = max(t.temperature for t in temps_7d) if temps_7d else latest_temp.temperature

        # История пожаров
        last_fire_date = self.fire_repo.get_last_fire_date_by_pile_id(pile.pile_id)
        if last_fire_date is None:
            days_since_last_fire = -1
            fire_history_count = 0
        else:
            days_since_last_fire = (forecast_date - last_fire_date).days
            # Пожары за последний год
            start_year = forecast_date - timedelta(days=365)
            fires_last_year = self.fire_repo.get_fires_in_date_range(start_year, forecast_date)
            fire_history_count = len(fires_last_year)

        # Погода
        weather = self.weather_repo.get_by_date(forecast_date)
        if not weather:
            return None

        # Сезонные признаки
        month = forecast_date.month
        if month in (3, 4, 5):
            season = 1
        elif month in (6, 7, 8):
            season = 2
        elif month in (9, 10, 11):
            season = 3
        else:
            season = 4

        import math
        month_sin = math.sin(2 * math.pi * month / 12)
        month_cos = math.cos(2 * math.pi * month / 12)

        return {
            "pile_id": pile.pile_id,
            "coal_type": pile.coal_type,
            "pile_formation_date": pile.formation_date.isoformat(),
            "initial_volume_tonnes": pile.initial_volume_tonnes,
            "days_in_storage": days_in_storage,
            "temperature_p": latest_temp.temperature,
            "temp_trend_7d": temp_trend_7d,
            "temp_avg_7d": temp_avg_7d,
            "temp_max_7d": temp_max_7d,
            "days_since_last_fire": days_since_last_fire,
            "fire_history_count": fire_history_count,
            "weather_temp_avg": weather.air_temperature,
            "weather_humidity": weather.humidity,
            "season": season,
            "month_sin": month_sin,
            "month_cos": month_cos,
        }

    # def _convert_to_predictions(self, ml_result: dict, warehouse_id: int) -> List[Prediction]:
    #     """Преобразует результат ML в список Prediction для сохранения в БД."""
    #     predictions = []
    #     base_date = date.fromisoformat(ml_result["forecast_date"])
    #     for i in range(1, 4):
    #         day_key = f"day_{i}"
    #         pred_date = base_date + timedelta(days=i - 1)
    #         predictions.append(
    #             Prediction(
    #                 pile_id=ml_result["pile_id"],
    #                 warehouse_id=warehouse_id,
    #                 prediction_date=base_date,
    #                 forecast_date=pred_date,
    #                 risk_level=ml_result["risk_levels"][day_key],
    #                 probability=ml_result["probabilities"][day_key],
    #             )
    #         )
    #     return predictions

    def _convert_to_predictions(self, ml_result: dict, warehouse_id: int, forecast_date: date) -> List[Prediction]:
        """Преобразует результат ML в список Prediction для сохранения в БД."""
        predictions = []
        for i in range(1, 4):
            day_key = f"day_{i}"
            pred_date = forecast_date + timedelta(days=i - 1)
            predictions.append(
                Prediction(
                    pile_id=ml_result["pile_id"],
                    warehouse_id=warehouse_id,
                    prediction_date=forecast_date,
                    forecast_date=pred_date,
                    risk_level=ml_result["risk_levels"][day_key],
                    probability=ml_result["probabilities"][day_key],
                )
            )
        return predictions