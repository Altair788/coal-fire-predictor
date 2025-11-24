# from fastapi import APIRouter
#
# router = APIRouter()
#
#
# @router.get("")
# def get_dashboard():
#     return {
#         "piles": [
#             {
#                 "pile_id": 1,
#                 "coal_type": "A1",
#                 "formation_date": "2025-10-01",
#                 "days_in_storage": 52,
#                 "last_temp": 38.6,
#                 "risk_forecast": {
#                     "2025-11-23": "low",
#                     "2025-11-24": "medium",
#                     "2025-11-25": "high",
#                 },
#             },
#             {
#                 "pile_id": 6,
#                 "coal_type": "B2",
#                 "formation_date": "2025-10-15",
#                 "days_in_storage": 38,
#                 "last_temp": 42.1,
#                 "risk_forecast": {
#                     "2025-11-23": "medium",
#                     "2025-11-24": "high",
#                     "2025-11-25": "high",
#                 },
#             },
#         ],
#         "weather_summary": {"temp_avg": 5.2, "humidity": 78},
#         "days_without_fire": 42,
#         "last_update": "2025-11-22T10:00:00Z",
#     }


from fastapi import APIRouter, Depends, HTTPException
from app.application.use_cases.get_dashboard_data import GetDashboardData
from app.core.dependencies import (
    get_coal_pile_repository,
    get_temperature_repository,
    get_prediction_repository,
    get_fire_incident_repository,
    get_weather_repository,
)

router = APIRouter()


@router.get("")
def get_dashboard(
    pile_repo=Depends(get_coal_pile_repository),
    temp_repo=Depends(get_temperature_repository),
    pred_repo=Depends(get_prediction_repository),
    fire_repo=Depends(get_fire_incident_repository),
    weather_repo=Depends(get_weather_repository),
):
    try:
        use_case = GetDashboardData(
            pile_repo=pile_repo,
            temp_repo=temp_repo,
            pred_repo=pred_repo,
            fire_repo=fire_repo,
            weather_repo=weather_repo,
        )
        return use_case.execute()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при формировании дашборда: {str(e)}"
        )