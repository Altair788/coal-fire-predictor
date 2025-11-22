from fastapi import APIRouter

router = APIRouter()

@router.get("")
def get_analytics():
    return {
        "metrics": {
            "precision": 0.35,
            "recall": 0.72,
            "f1_score": 0.47,
            "pr_auc": 0.58
        },
        "fire_events": [
            {
                "pile_id": 15,
                "actual_date": "2025-11-20",
                "predicted_interval": ["2025-11-17", "2025-11-19"],
                "hit": True
            },
            {
                "pile_id": 6,
                "actual_date": "2025-11-25",
                "predicted_interval": ["2025-11-22", "2025-11-24"],
                "hit": False
            }
        ]
    }