from fastapi import APIRouter, File, Form, HTTPException, UploadFile

router = APIRouter()

ALLOWED_DATA_TYPES = {"temperatures", "fires", "supplies", "weather"}


@router.post("")
def upload_data(
    file: UploadFile = File(...),
    data_type: str = Form(...),
):
    if data_type not in ALLOWED_DATA_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый тип данных. Допустимые значения: {sorted(ALLOWED_DATA_TYPES)}",
        )

    # здесь будет вызов реального Use Case пока заглушка
    return {
        "status": "success",
        "message": f"Данные типа '{data_type}' приняты. Прогноз обновляется.",
    }
