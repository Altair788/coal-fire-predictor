# from fastapi import APIRouter, Path
#
# router = APIRouter()
#
#
# @router.get("/{pile_id}/history")
# def get_pile_history(pile_id: int = Path(...)):
#     return {
#         "pile_id": pile_id,
#         "coal_type": "A1",
#         "formation_date": "2025-10-01",
#         "days_in_storage": 52,
#         "last_temp": 40.1,
#         "temperature_history": [
#             {"date": "2025-11-10", "temp": 32.1},
#             {"date": "2025-11-12", "temp": 33.5},
#             {"date": "2025-11-15", "temp": 35.7},
#             {"date": "2025-11-18", "temp": 38.2},
#             {"date": "2025-11-20", "temp": 40.1},
#         ],
#         "risk_history": [
#             {"date": "2025-11-15", "level": "low", "probability": 0.08},
#             {"date": "2025-11-18", "level": "medium", "probability": 0.35},
#             {"date": "2025-11-20", "level": "high", "probability": 0.78},
#             {"date": "2025-11-22", "level": "high", "probability": 0.85},
#         ],
#     }


from fastapi import APIRouter, Path, Depends, HTTPException
from app.application.use_cases.get_pile_history import GetPileHistory
from app.core.dependencies import (
    get_coal_pile_repository,
    get_temperature_repository,
    get_prediction_repository,
)

router = APIRouter()


@router.get("/{pile_id}/history")
def get_pile_history(
    pile_id: int = Path(..., description="Уникальный ID штабеля"),
    pile_repo=Depends(get_coal_pile_repository),
    temp_repo=Depends(get_temperature_repository),
    pred_repo=Depends(get_prediction_repository),
):
    try:
        use_case = GetPileHistory(
            pile_repo=pile_repo,
            temp_repo=temp_repo,
            pred_repo=pred_repo,
        )
        return use_case.execute(pile_id=pile_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении истории: {str(e)}")