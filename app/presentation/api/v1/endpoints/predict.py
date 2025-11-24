from datetime import date as dt_date
from typing import List, Optional, Union

from fastapi import APIRouter, Query, Depends, HTTPException
from app.application.use_cases.calculate_fire_risk import CalculateFireRisk
from app.core.dependencies import get_calculate_fire_risk

router = APIRouter()


@router.get("")
def get_prediction(
    pile_id: Optional[int] = Query(None),
    date: Optional[str] = Query(None, alias="forecast_date_str"),  # опционально можно оставить alias
    calculate_service: CalculateFireRisk = Depends(get_calculate_fire_risk),
) -> Union[dict, List[dict]]:
    """
    Получение прогноза риска самовозгорания.
    Если параметр `date` не указан — дата определяется автоматически
    по последней доступной температуре в системе.
    """
    # Определяем forecast_date_for_use_case
    if date is not None:
        try:
            forecast_date_for_use_case = dt_date.fromisoformat(date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Неверный формат даты. Используйте YYYY-MM-DD."
            )
    else:
        forecast_date_for_use_case = None  # ← КЛЮЧЕВОЕ: передаём None

    try:
        forecasts = calculate_service.execute(forecast_date=forecast_date_for_use_case)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при расчёте прогноза: {str(e)}")

    if pile_id is not None:
        for f in forecasts:
            if f.pile_id == pile_id:
                return f.model_dump()
        raise HTTPException(status_code=404, detail=f"Прогноз для штабеля {pile_id} не найден.")

    return [f.model_dump() for f in forecasts]