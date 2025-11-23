# from typing import Optional
#
# from fastapi import APIRouter, Query
#
# router = APIRouter()
#
#
# @router.get("")
# def get_prediction(
#     pile_id: Optional[int] = Query(None), date: Optional[str] = Query(None)
# ):
#     if pile_id is not None:
#         return {
#             "pile_id": pile_id,
#             "forecast_date": date or "2025-11-23",
#             "risk_levels": {"day_1": "low", "day_2": "medium", "day_3": "high"},
#             "probabilities": {"day_1": 0.12, "day_2": 0.45, "day_3": 0.81},
#         }
#     else:
#         return [
#             {
#                 "pile_id": 1,
#                 "forecast_date": "2025-11-23",
#                 "risk_levels": {"day_1": "low", "day_2": "medium", "day_3": "high"},
#                 "probabilities": {"day_1": 0.12, "day_2": 0.45, "day_3": 0.81},
#             },
#             {
#                 "pile_id": 6,
#                 "forecast_date": "2025-11-23",
#                 "risk_levels": {"day_1": "medium", "day_2": "high", "day_3": "high"},
#                 "probabilities": {"day_1": 0.35, "day_2": 0.72, "day_3": 0.88},
#             },
#         ]


from datetime import date as dt_date
from typing import List, Optional, Union

from fastapi import APIRouter, Query, Depends, HTTPException
from app.application.use_cases.calculate_fire_risk import CalculateFireRisk
from app.core.dependencies import get_calculate_fire_risk
from app.domain.entities import RiskForecast

router = APIRouter()


@router.get("")
def get_prediction(
    pile_id: Optional[int] = Query(None),
    forecast_date_str: Optional[str] = Query(None),
    calculate_service: CalculateFireRisk = Depends(get_calculate_fire_risk),
) -> Union[RiskForecast, List[RiskForecast]]:
    """
    Получение прогноза риска самовозгорания.
    Если pile_id не указан — возвращает прогнозы для всех активных штабелей.
    """
    # Парсинг даты
    forecast_date = dt_date.today()
    if forecast_date_str:
        try:
            forecast_date = dt_date.fromisoformat(forecast_date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты. Используйте YYYY-MM-DD.")

    # Выполнение прогноза
    try:
        forecasts = calculate_service.execute(forecast_date=forecast_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при расчёте прогноза: {str(e)}")

    # Фильтрация по pile_id, если задан
    if pile_id is not None:
        for f in forecasts:
            if f.pile_id == pile_id:
                return f.model_dump()
        raise HTTPException(status_code=404, detail=f"Прогноз для штабеля {pile_id} не найден.")

    # Возвращаем список для всех штабелей
    return [f.model_dump() for f in forecasts]