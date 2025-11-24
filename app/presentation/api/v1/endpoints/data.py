# from fastapi import APIRouter, File, Form, HTTPException, UploadFile
#
# router = APIRouter()
#
# ALLOWED_DATA_TYPES = {"temperature", "fires", "supplies", "weather"}
#
#
# @router.post("")
# def upload_data(
#     file: UploadFile = File(...),
#     data_type: str = Form(...),
# ):
#     if data_type not in ALLOWED_DATA_TYPES:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Недопустимый тип данных. Допустимые значения: {sorted(ALLOWED_DATA_TYPES)}",
#         )
#
#     # здесь будет вызов реального Use Case пока заглушка
#     return {
#         "status": "success",
#         "message": f"Данные типа '{data_type}' приняты. Прогноз обновляется.",
#     }


from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from io import TextIOWrapper
from app.application.use_cases.upload_data import UploadDataService
from app.core.dependencies import (
    get_temperature_repository,
    get_fire_incident_repository,
    get_coal_pile_repository,
    get_weather_repository,
)

router = APIRouter()

ALLOWED_DATA_TYPES = {"temperature", "fires", "supplies", "weather"}


@router.post("")
def upload_data(
    file: UploadFile = File(...),
    data_type: str = Form(...),
    pile_repo=Depends(get_coal_pile_repository),
    temp_repo=Depends(get_temperature_repository),
    fire_repo=Depends(get_fire_incident_repository),
    weather_repo=Depends(get_weather_repository),
):
    if data_type not in ALLOWED_DATA_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый тип данных. Допустимые значения: {sorted(ALLOWED_DATA_TYPES)}"
        )

    if file.content_type not in ("text/csv", "application/vnd.ms-excel"):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате CSV")

    try:
        content = file.file.read().decode("utf-8")
        from io import StringIO
        file_like = StringIO(content)

        service = UploadDataService(
            temperature_repo=temp_repo,
            fire_repo=fire_repo,
            pile_repo=pile_repo,
            weather_repo=weather_repo,
        )
        service.upload_csv(file_like, data_type)

        return {
            "status": "success",
            "message": f"Данные типа '{data_type}' приняты. Прогноз обновляется."
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка в данных: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")