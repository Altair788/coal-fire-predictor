from datetime import date, datetime, timedelta
from typing import List

from app.domain.entities import CoalPile, TemperatureReading, Prediction
from app.domain.interfaces import (
    CoalPileRepository,
    TemperatureRepository,
    PredictionRepository,
    FireIncidentRepository,
    WeatherRepository,
)


class GetDashboardData:
    """
    Use Case для сбора данных главного экрана (Dashboard).
    """

    def __init__(
        self,
        pile_repo: CoalPileRepository,
        temp_repo: TemperatureRepository,
        pred_repo: PredictionRepository,
        fire_repo: FireIncidentRepository,
        weather_repo: WeatherRepository,
    ):
        self.pile_repo = pile_repo
        self.temp_repo = temp_repo
        self.pred_repo = pred_repo
        self.fire_repo = fire_repo
        self.weather_repo = weather_repo

    def execute(self, forecast_date: date = None) -> dict:
        if forecast_date is None:
            forecast_date = date.today()

        # 1. Все активные штабели
        piles = self.pile_repo.get_all_active()
        piles_data = []

        for pile in piles:
            # Последняя температура
            latest_temp = self.temp_repo.get_latest_by_pile_id(pile.pile_id)
            if not latest_temp:
                continue

            # Прогнозы на 3 дня (base_date = forecast_date)
            pred_dates = [forecast_date, forecast_date + timedelta(days=1), forecast_date + timedelta(days=2)]
            predictions = self.pred_repo.get_by_pile_id_and_forecast_dates(pile.pile_id, pred_dates)

            # Формируем risk_forecast: {"2025-11-23": "low", ...}
            risk_forecast = {}
            for i, d in enumerate(pred_dates):
                day_key = f"day_{i+1}"
                # Ищем прогноз на эту дату
                pred = next((p for p in predictions if p.forecast_date == d), None)
                risk_level = pred.risk_level if pred else "low"
                risk_forecast[d.isoformat()] = risk_level

            piles_data.append({
                "pile_id": pile.pile_id,
                "coal_type": pile.coal_type,
                "formation_date": pile.formation_date.isoformat(),
                "days_in_storage": (forecast_date - pile.formation_date).days,
                "last_temp": float(latest_temp.temperature),
                "risk_forecast": risk_forecast,
            })

        # 2. Сводка по погоде на сегодня
        weather = self.weather_repo.get_by_date(forecast_date)
        weather_summary = {
            "temp_avg": weather.air_temperature if weather else 0.0,
            "humidity": weather.humidity if weather else 0.0,
        }

        # 3. Дни без пожаров
        last_fire = self._get_last_fire_date()
        if last_fire:
            days_without_fire = (forecast_date - last_fire).days
        else:
            days_without_fire = 999  # или 0, по логике ТЗ

        return {
            "piles": piles_data,
            "weather_summary": weather_summary,
            "days_without_fire": days_without_fire,
            "last_update": datetime.utcnow().isoformat() + "Z",
        }

    def _get_last_fire_date(self) -> date | None:
        """Получает дату последнего пожара во всей БД."""
        piles = self.pile_repo.get_all_active()
        last_dates = []
        for pile in piles:
            d = self.fire_repo.get_last_fire_date_by_pile_id(pile.pile_id)
            if d:
                last_dates.append(d)
        return max(last_dates) if last_dates else None