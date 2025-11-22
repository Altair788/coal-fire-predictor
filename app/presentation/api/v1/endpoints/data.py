from fastapi import APIRouter, File, UploadFile, Form

router = APIRouter()

@router.post("/post")
def upload_data(
    file: UploadFile = File(...),
    data_type: str = Form(...)
):
    return {
        "status": "success",
        "message": f"Данные типа '{data_type}' приняты. Прогноз обновляется."
    }