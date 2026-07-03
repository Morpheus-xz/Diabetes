"""Prediction and explanation helpers for API layer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
]


@dataclass
class PredictionResult:
    """Structured prediction output for API and chatbot context."""

    prediction: int
    probability: float
    risk_level: str
    explanation: str
    top_contributors: list[tuple[str, float]]


class DiabetesPredictor:
    """Load trained models and serve predictions with simple explanations."""

    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or Path(__file__).resolve().parents[2]
        self.model_dir = self.root_dir / "model"
        self.model_path = self.model_dir / "model.pkl"
        self.scaler_path = self.model_dir / "scaler.pkl"
        self.rf_model_path = self.model_dir / "rf_model.pkl"
        self.stats_path = self.model_dir / "feature_stats.csv"

        self.model: Any | None = None
        self.scaler: Any | None = None
        self.rf_model: Any | None = None
        self.feature_stats: pd.DataFrame | None = None
        self.is_loaded = False

        self._load_artifacts()

    def _load_artifacts(self) -> None:
        if not (self.model_path.exists() and self.scaler_path.exists()):
            return
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        self.rf_model = joblib.load(self.rf_model_path) if self.rf_model_path.exists() else None
        self.feature_stats = pd.read_csv(self.stats_path) if self.stats_path.exists() else None
        self.is_loaded = True

    @staticmethod
    def _risk_from_probability(probability: float) -> str:
        if probability < 0.35:
            return "Low"
        if probability < 0.65:
            return "Moderate"
        return "High"

    def _prepare_input(self, payload: dict[str, float]) -> pd.DataFrame:
        missing = [col for col in FEATURE_COLUMNS if col not in payload]
        if missing:
            raise ValueError(f"Missing input values: {', '.join(missing)}")
        return pd.DataFrame([[payload[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)

    def _predict_probability(self, x_df: pd.DataFrame) -> float:
        assert self.model is not None
        assert self.scaler is not None

        model_name = type(self.model).__name__.lower()
        if "logistic" in model_name or "svc" in model_name:
            x_input: Any = self.scaler.transform(x_df)
        else:
            x_input = x_df

        probability = float(self.model.predict_proba(x_input)[0, 1])
        return max(0.0, min(1.0, probability))

    def _top_feature_contributors(
        self, payload: dict[str, float], top_k: int = 3
    ) -> list[tuple[str, float]]:
        if self.rf_model is None or self.feature_stats is None:
            return []

        importance = np.asarray(self.rf_model.feature_importances_, dtype=float)
        stats = self.feature_stats.set_index("feature")

        contrib: list[tuple[str, float]] = []
        for idx, feature in enumerate(FEATURE_COLUMNS):
            mean_val = float(stats.loc[feature, "mean"]) if feature in stats.index else 0.0
            std_val = float(stats.loc[feature, "std"]) if feature in stats.index else 1.0
            std_val = std_val if std_val != 0 else 1.0
            normalized_distance = abs((float(payload[feature]) - mean_val) / std_val)
            score = float(importance[idx]) * normalized_distance
            contrib.append((feature, score))

        contrib.sort(key=lambda item: item[1], reverse=True)
        return contrib[:top_k]

    def _generate_explanation(
        self, payload: dict[str, float], risk_level: str
    ) -> tuple[str, list[tuple[str, float]]]:
        top = self._top_feature_contributors(payload)
        if not top:
            return (
                "This result is estimated from the combined pattern of all health indicators. "
                "Higher glucose, BMI, and age generally increase risk.",
                [],
            )

        readable = []
        for feature, _ in top:
            raw = payload[feature]
            if feature == "Glucose":
                readable.append(f"glucose ({raw})")
            elif feature == "BMI":
                readable.append(f"BMI ({raw:.1f})")
            elif feature == "DiabetesPedigreeFunction":
                readable.append(f"diabetes pedigree score ({raw:.2f})")
            else:
                readable.append(f"{feature.lower()} ({raw})")

        level_msg = {
            "Low": "currently suggests a lower likelihood",
            "Moderate": "indicates a moderate likelihood",
            "High": "suggests a higher likelihood",
        }[risk_level]
        text = (
            f"The model {level_msg} of diabetes risk. "
            f"The strongest contributing factors were {', '.join(readable)}."
        )
        return text, top

    def predict(self, payload: dict[str, float]) -> PredictionResult:
        if not self.is_loaded:
            raise FileNotFoundError(
                "Model artifacts are missing. Run `python model/train_model.py` after placing "
                "the dataset in `data/diabetes.csv`."
            )

        x_df = self._prepare_input(payload)
        probability = self._predict_probability(x_df)
        prediction = int(probability >= 0.5)
        risk_level = self._risk_from_probability(probability)
        explanation, top_contributors = self._generate_explanation(payload, risk_level)

        return PredictionResult(
            prediction=prediction,
            probability=probability,
            risk_level=risk_level,
            explanation=explanation,
            top_contributors=top_contributors,
        )

