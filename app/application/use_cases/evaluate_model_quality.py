from datetime import date, timedelta
from typing import List, Dict, Any

from app.domain.interfaces import PredictionRepository, FireIncidentRepository


class EvaluateModelQuality:
    """
    Use Case для оценки качества модели прогнозирования.
    Выполняет сравнение прогнозов с реальными возгораниями и расчёт метрик.
    """

    def __init__(
        self,
        prediction_repo: PredictionRepository,
        fire_repo: FireIncidentRepository,
    ):
        self.prediction_repo = prediction_repo
        self.fire_repo = fire_repo

    def execute(self, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        # Получаем все прогнозы с уровнем 'high' через репозиторий
        all_high_predictions = self.prediction_repo.get_all_high_risk_predictions(
            start_date=start_date, end_date=end_date
        )
        all_fires = self.fire_repo.get_fires_in_date_range(
            start_date or date.min, end_date or date.max
        )

        # Преобразуем пожары в словарь для поиска по (pile_id, date)
        fire_set = {(f.pile_id, f.actual_date) for f in all_fires}

        fire_events = []
        hits = 0
        total_predictions = 0

        for pred in all_high_predictions:
            total_predictions += 1
            hit = False

            # Проверяем, было ли возгорание в окне [D+1, D+3]
            for days_ahead in range(1, 4):
                check_date = pred.forecast_date + timedelta(days=days_ahead)
                if (pred.pile_id, check_date) in fire_set:
                    hit = True
                    hits += 1
                    break

            # Формируем запись события
            fire_events.append({
                "pile_id": pred.pile_id,
                "actual_date": (pred.forecast_date + timedelta(days=1)).isoformat() if hit else None,
                "predicted_interval": [
                    (pred.forecast_date + timedelta(days=1)).isoformat(),
                    (pred.forecast_date + timedelta(days=3)).isoformat(),
                ],
                "hit": hit,
            })

        # Расчёт метрик
        true_positives = hits
        false_positives = total_predictions - hits
        false_negatives = len(all_fires) - true_positives

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # PR-AUC — заглушка из ml/metrics.json (или можно читать файл)
        pr_auc = self._load_pr_auc_from_file()

        return {
            "metrics": {
                "precision": round(precision, 2),
                "recall": round(recall, 2),
                "f1_score": round(f1_score, 2),
                "pr_auc": pr_auc,
            },
            "fire_events": fire_events,
        }

    def _load_pr_auc_from_file(self) -> float:
        """Читает PR-AUC из ml/metrics.json, как указано в ТЗ."""
        try:
            import json
            from pathlib import Path
            metrics_path = Path("ml/metrics.json")
            if metrics_path.exists():
                with open(metrics_path, "r", encoding="utf-8") as f:
                    metrics = json.load(f)
                return float(metrics.get("pr_auc", 0.5))
        except Exception:
            pass
        return 0.58  # значение по умолчанию из ТЗ