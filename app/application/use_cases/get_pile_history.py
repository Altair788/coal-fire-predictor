from datetime import date
from typing import List

from app.domain.entities import CoalPile, TemperatureReading, Prediction
from app.domain.interfaces import (
    CoalPileRepository,
    TemperatureRepository,
    PredictionRepository,
)


class GetPileHistory:
    """
    Use Case для получения истории температуры и прогнозов по штабелю.
    """

    def __init__(
        self,
        pile_repo: CoalPileRepository,
        temp_repo: TemperatureRepository,
        pred_repo: PredictionRepository,
    ):
        self.pile_repo = pile_repo
        self.temp_repo = temp_repo
        self.pred_repo = pred_repo

    def execute(self, pile_id: int, forecast_date: date = None) -> dict:
        if forecast_date is None:
            forecast_date = date.today()

        # 1. Данные о штабеле
        pile = self.pile_repo.get_by_id(pile_id)
        if not pile:
            raise ValueError(f"Штабель с pile_id={pile_id} не найден")

        # 2. История температур
        temp_history = self.temp_repo.get_by_pile_id_and_date_range(
            pile_id, start_date=date.min, end_date=forecast_date
        )
        temperature_history = [
            {"date": t.measurement_date.isoformat(), "temp": float(t.temperature)}
            for t in temp_history
        ]
        temperature_history.sort(key=lambda x: x["date"])

        # 3. Последняя температура
        last_temp = temperature_history[-1]["temp"] if temperature_history else 0.0

        # 4. История прогнозов — получаем ВСЕ прогнозы для этого штабеля
        all_predictions = self.pred_repo.get_all_by_pile_id(pile_id)
        risk_history = []
        for p in all_predictions:
            level = p.risk_level.lower() if p.risk_level else "low"
            risk_history.append({
                "date": p.forecast_date.isoformat(),
                "level": level,
                "probability": float(p.probability),
            })
        risk_history.sort(key=lambda x: x["date"])

        return {
            "pile_id": pile.pile_id,
            "coal_type": pile.coal_type,
            "formation_date": pile.formation_date.isoformat(),
            "days_in_storage": (forecast_date - pile.formation_date).days,
            "last_temp": last_temp,
            "temperature_history": temperature_history,
            "risk_history": risk_history,
        }