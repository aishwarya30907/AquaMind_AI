from __future__ import annotations

import json
from pathlib import Path

import joblib

from app.config import settings


class ModelUnavailableError(RuntimeError):
    pass


class HABModel:
    def __init__(self) -> None:
        self.model = None
        self.error = None
        self.model_path = self._resolve_model_path()
        self._load_model()

    def _resolve_model_path(self) -> str | None:
        for candidate in settings.HAB_MODEL_CANDIDATES:
            if not candidate:
                continue
            path = Path(candidate)
            if path.exists():
                return str(path)
        return None

    def is_available(self) -> bool:
        return self.model is not None

    def _load_model(self) -> None:
        model_path = self._resolve_model_path()
        if model_path is None:
            self.error = (
                'HAB model is not available. Place a trained model at backend/models/hab_model.joblib '
                'or set HAB_MODEL_PATH.'
            )
            return

        try:
            self.model = joblib.load(model_path)
            self.model_path = model_path
            self.error = None
        except Exception as exc:  # pragma: no cover - depends on actual model asset
            self.model = None
            self.error = f'Unable to load HAB model: {exc}'

    def _fallback_prediction(self, features: dict) -> dict:
        temp = float(features.get('temperature', 0.0) or 0.0)
        chlorophyll = float(features.get('chlorophyll', 0.0) or 0.0)
        nitrate = float(features.get('nitrate', 0.0) or 0.0)
        salinity = float(features.get('salinity', 0.0) or 0.0)
        ph = float(features.get('ph', 0.0) or 0.0)
        dissolved_oxygen = float(features.get('dissolved_oxygen', 0.0) or 0.0)

        score = 0.0
        score += max(0.0, chlorophyll - 10) * 0.05
        score += max(0.0, nitrate - 1.5) * 0.2
        score += max(0.0, temp - 24) * 0.15
        score += max(0.0, salinity - 25) * 0.02
        score += max(0.0, 8.0 - ph) * 0.0 if ph else 0.0
        score += max(0.0, 8.0 - dissolved_oxygen) * 0.1

        if score >= 10:
            risk = 'High'
            confidence = 0.88
            probabilities = {'Low': 0.12, 'Medium': 0.24, 'High': 0.64}
        elif score >= 5:
            risk = 'Medium'
            confidence = 0.71
            probabilities = {'Low': 0.22, 'Medium': 0.48, 'High': 0.30}
        else:
            risk = 'Low'
            confidence = 0.66
            probabilities = {'Low': 0.58, 'Medium': 0.28, 'High': 0.14}

        return {
            'prediction': risk,
            'risk_level': risk,
            'confidence': confidence,
            'probabilities': probabilities,
            'model': 'hab_predictor_fallback',
            'warning': 'No trained HAB model file was found in the project. This result is a transparent fallback heuristic pending model placement.',
        }

    def predict(self, features: dict) -> dict:
        if self.model is None:
            return self._fallback_prediction(features)

        if hasattr(self.model, 'predict_proba'):
            vector = [features.get(name, 0.0) for name in self.model.feature_names_in_]
            probabilities = self.model.predict_proba([vector])[0]
            class_names = list(getattr(self.model, 'classes_', []))
            if not class_names:
                class_names = ['Low', 'Medium', 'High']
            category_index = int(self.model.predict([vector])[0]) if hasattr(self.model, 'predict') else 0
            label = class_names[category_index] if category_index < len(class_names) else class_names[-1]
            return {
                'prediction': label,
                'risk_level': label,
                'confidence': float(max(probabilities)) if probabilities.size else 0.0,
                'probabilities': {str(cls): float(prob) for cls, prob in zip(class_names, probabilities)},
                'model': 'hab_predictor',
            }

        prediction = str(self.model.predict([list(features.values())])[0])
        return {
            'prediction': prediction,
            'risk_level': prediction,
            'confidence': 0.0,
            'probabilities': {},
            'model': 'hab_predictor',
        }


hab_model = HABModel()
