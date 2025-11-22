from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("")
def get_prediction(
        pile_id: Optional[int] = Query(None),
        date: Optional[str] = Query(None)
):
    if pile_id is not None:
        return {
            "pile_id": pile_id,
            "forecast_date": date or "2025-11-23",
            "risk_levels": {
                "day_1": "low",
                "day_2": "medium",
                "day_3": "high"
            },
            "probabilities": {
                "day_1": 0.12,
                "day_2": 0.45,
                "day_3": 0.81
            }
        }
    else:
        return [
            {
                "pile_id": 1,
                "forecast_date": "2025-11-23",
                "risk_levels": {"day_1": "low", "day_2": "medium", "day_3": "high"},
                "probabilities": {"day_1": 0.12, "day_2": 0.45, "day_3": 0.81}
            },
            {
                "pile_id": 6,
                "forecast_date": "2025-11-23",
                "risk_levels": {"day_1": "medium", "day_2": "high", "day_3": "high"},
                "probabilities": {"day_1": 0.35, "day_2": 0.72, "day_3": 0.88}
            }
        ]
