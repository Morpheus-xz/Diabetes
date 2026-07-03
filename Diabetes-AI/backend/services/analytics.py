"""Analytics data loaders for frontend dashboards."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class AnalyticsService:
    """Serve model/dataset analytics from persisted artifacts."""

    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or Path(__file__).resolve().parents[2]
        self.model_dir = self.root_dir / "model"
        self.data_path = self.root_dir / "data" / "diabetes.csv"

    def dataset_summary(self) -> dict[str, Any]:
        if not self.data_path.exists():
            return {"available": False}
        df = pd.read_csv(self.data_path)
        if "Outcome" not in df.columns:
            return {"available": False}
        summary = {
            "available": True,
            "records": int(len(df)),
            "positive_cases": int(df["Outcome"].sum()),
            "avg_glucose": float(df["Glucose"].replace(0, np.nan).fillna(df["Glucose"].median()).mean()),
            "avg_bmi": float(df["BMI"].replace(0, np.nan).fillna(df["BMI"].median()).mean()),
            "statistics": df.describe().replace({np.nan: None}).to_dict(),
            "columns": list(df.columns),
        }
        return summary

    def model_comparison(self) -> list[dict[str, Any]]:
        path = self.model_dir / "model_comparison.csv"
        if not path.exists():
            return []
        return pd.read_csv(path).to_dict(orient="records")

    def feature_importance(self) -> list[dict[str, Any]]:
        path = self.model_dir / "rf_feature_importance.csv"
        if not path.exists():
            return []
        return pd.read_csv(path).to_dict(orient="records")

    def confusion_matrix(self) -> list[list[int]]:
        path = self.model_dir / "confusion_matrix.npy"
        if not path.exists():
            return []
        matrix = np.load(path)
        return matrix.astype(int).tolist()

    def roc_curve(self) -> dict[str, list[float]]:
        path = self.model_dir / "roc_curve.npz"
        if not path.exists():
            return {"fpr": [], "tpr": []}
        roc = np.load(path)
        return {
            "fpr": [float(value) for value in roc["fpr"]],
            "tpr": [float(value) for value in roc["tpr"]],
        }

    def best_model_metrics(self) -> dict[str, Any]:
        path = self.model_dir / "best_model_metrics.json"
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

