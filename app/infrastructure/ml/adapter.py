import logging
from pathlib import Path
from typing import Any, Dict

from app.domain.interfaces import MLService
from app.core.config import settings

try:
    from ml.predict import predict_risk as _predict_risk
except ImportError as e:
    raise ImportError(
        "Не удалось загрузить ML-модуль. Убедитесь, что файл `ml/predict.py` существует "
        "и содержит функцию `predict_risk`."
    ) from e

logger = logging.getLogger(__name__)


class MLModelAdapter(MLService):
    """
    Адаптер для вызова ML-модели.
    Обеспечивает изоляцию ML-логики от остальной системы.
    """

    def __init__(self, model_path: str = "ml/models/final_model.joblib"):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            logger.warning(f"Модель не найдена по пути: {self.model_path}")
        # Модель загрузится при первом вызове predict_risk из ml/predict.py

    def predict_risk(self, pile_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Вызывает синхронную функцию predict_risk из ml/predict.py.
        Гарантирует соответствие контракту с дата-сайентистом.
        """
        try:
            result = _predict_risk(pile_features)
            logger.debug(f"ML-прогноз получен для pile_id={result.get('pile_id')}")
            return result
        except Exception as e:
            logger.error(f"Ошибка при вызове ML-модели: {e}")
            raise ValueError(f"ML-модель вернула ошибку: {e}") from e