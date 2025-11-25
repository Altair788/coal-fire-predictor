import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

_MODEL_PATH = Path(__file__).parent / "models" / "final_model.joblib"


class CoalFirePredictor:
    def __init__(self, model_path=_MODEL_PATH):
        try:
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
        except Exception as e:
            raise ValueError(f"Ошибка загрузки модели: {e}")

    def _prepare_features(self, pile_features):
        feature_dict = {}
        for feature in self.feature_columns:
            feature_dict[feature] = [pile_features.get(feature, 0)]

        df = pd.DataFrame(feature_dict)

        df_scaled = self.scaler.transform(df)

        return df_scaled

    def _map_risk_level(self, probability):
        if probability < 0.005: # 0.3
            return "low"
        elif probability < 0.01: # 0.7
            return "medium"
        else:
            return "high"

    def predict_risk(self, pile_features):

        try:
            X = self._prepare_features(pile_features)

            probability = self.model.predict_proba(X)[0, 1]

            probabilities = {
                'day_1': min(probability * 1.0, 0.99),
                'day_2': min(probability * 0.9, 0.99),
                'day_3': min(probability * 0.8, 0.99)
            }

            risk_levels = {
                day: self._map_risk_level(prob)
                for day, prob in probabilities.items()
            }

            result = {
                "pile_id": pile_features.get('pile_id', 0),
                "forecast_date": pile_features.get("forecast_date", datetime.now().strftime('%Y-%m-%d')),
                "risk_levels": risk_levels,
                "probabilities": probabilities
            }

            return result

        except Exception as e:
            raise ValueError(f"Ошибка предсказания: {e}")


_predictor = None


def predict_risk(pile_features):
    global _predictor
    if _predictor is None:
        _predictor = CoalFirePredictor()
    return _predictor.predict_risk(pile_features)
