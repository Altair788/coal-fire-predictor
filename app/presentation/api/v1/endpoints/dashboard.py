from fastapi import APIRouter

router = APIRouter()


@router.get("")
def get_dashboard():
    return {
        "piles": [
            {
                "pile_id": 1,
                "coal_type": "A1",
                "formation_date": "2025-10-01",
                "days_in_storage": 52,
                "last_temp": 38.6,
                "risk_forecast": {
                    "2025-11-23": "low",
                    "2025-11-24": "medium",
                    "2025-11-25": "high",
                },
            },
            {
                "pile_id": 6,
                "coal_type": "B2",
                "formation_date": "2025-10-15",
                "days_in_storage": 38,
                "last_temp": 42.1,
                "risk_forecast": {
                    "2025-11-23": "medium",
                    "2025-11-24": "high",
                    "2025-11-25": "high",
                },
            },
        ],
        "weather_summary": {"temp_avg": 5.2, "humidity": 78},
        "days_without_fire": 42,
        "last_update": "2025-11-22T10:00:00Z",
    }
