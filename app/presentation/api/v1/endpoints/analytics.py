# from fastapi import APIRouter
#
# router = APIRouter()
#
#
# @router.get("")
# def get_analytics():
#     return {
#         "metrics": {
#             "precision": 0.35,
#             "recall": 0.72,
#             "f1_score": 0.47,
#             "pr_auc": 0.58,
#         },
#         "fire_events": [
#             {
#                 "pile_id": 15,
#                 "actual_date": "2025-11-20",
#                 "predicted_interval": ["2025-11-17", "2025-11-19"],
#                 "hit": True,
#             },
#             {
#                 "pile_id": 6,
#                 "actual_date": "2025-11-25",
#                 "predicted_interval": ["2025-11-22", "2025-11-24"],
#                 "hit": False,
#             },
#         ],
#     }


from fastapi import APIRouter, Depends, HTTPException
from app.application.use_cases.evaluate_model_quality import EvaluateModelQuality
from app.core.dependencies import (
    get_prediction_repository,
    get_fire_incident_repository,
)

router = APIRouter()


@router.get("")
def get_analytics(
    pred_repo=Depends(get_prediction_repository),
    fire_repo=Depends(get_fire_incident_repository),
):
    try:
        use_case = EvaluateModelQuality(
            prediction_repo=pred_repo,
            fire_repo=fire_repo,
        )
        return use_case.execute()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при расчёте метрик качества: {str(e)}"
        )