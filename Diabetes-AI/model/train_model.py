"""Training pipeline for diabetes risk prediction models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "model"

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
TARGET_COLUMN = "Outcome"

ZERO_AS_MISSING = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]


def find_dataset_path() -> Path:
    """Return first matching dataset path from expected filenames."""
    candidates = [
        DATA_DIR / "diabetes.csv",
        DATA_DIR / "pima_diabetes.csv",
        DATA_DIR / "pima-indians-diabetes.csv",
    ]
    for path in candidates:
        if path.exists():
            return path

    message = (
        "Dataset not found.\n"
        "Place the PIMA Indians Diabetes dataset in:\n"
        f"- {DATA_DIR / 'diabetes.csv'}\n"
        "Expected columns: Pregnancies, Glucose, BloodPressure, SkinThickness, "
        "Insulin, BMI, DiabetesPedigreeFunction, Age, Outcome"
    )
    raise FileNotFoundError(message)


def validate_dataset_columns(df: pd.DataFrame) -> None:
    """Validate all required columns are present."""
    required = set(FEATURE_COLUMNS + [TARGET_COLUMN])
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(missing)
            + f"\nExpected columns: {', '.join(FEATURE_COLUMNS + [TARGET_COLUMN])}"
        )


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean missing values and enforce target shape."""
    clean_df = df.copy()

    for col in ZERO_AS_MISSING:
        clean_df[col] = clean_df[col].replace(0, np.nan)

    feature_medians = clean_df[FEATURE_COLUMNS].median(numeric_only=True)
    clean_df[FEATURE_COLUMNS] = clean_df[FEATURE_COLUMNS].fillna(feature_medians)

    clean_df = clean_df.dropna(subset=[TARGET_COLUMN])
    clean_df[TARGET_COLUMN] = clean_df[TARGET_COLUMN].astype(int)
    clean_df = clean_df[clean_df[TARGET_COLUMN].isin([0, 1])]
    return clean_df


def evaluate_model(
    model: Any,
    x_train: pd.DataFrame | np.ndarray,
    x_test: pd.DataFrame | np.ndarray,
    y_train: pd.Series,
    y_test: pd.Series,
) -> tuple[dict[str, float], np.ndarray, np.ndarray]:
    """Fit and evaluate model with core metrics."""
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    y_prob = model.predict_proba(x_test)[:, 1]

    metrics = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, zero_division=0),
        "Recall": recall_score(y_test, y_pred, zero_division=0),
        "F1 Score": f1_score(y_test, y_pred, zero_division=0),
        "ROC-AUC": roc_auc_score(y_test, y_prob),
    }
    return metrics, y_pred, y_prob


def save_correlation_heatmap(df: pd.DataFrame) -> None:
    """Save a static heatmap image for README/screenshots support."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    corr = df[FEATURE_COLUMNS + [TARGET_COLUMN]].corr(numeric_only=True)
    plt.figure(figsize=(10, 7))
    sns.heatmap(corr, annot=True, cmap="Blues", fmt=".2f", square=False)
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(MODEL_DIR / "correlation_heatmap.png", dpi=180)
    plt.close()


def train() -> None:
    """Train multiple models and persist the best one and analytics artifacts."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    dataset_path = find_dataset_path()
    raw_df = pd.read_csv(dataset_path)
    validate_dataset_columns(raw_df)
    df = clean_data(raw_df)

    x = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    models = {
        "Logistic Regression": (LogisticRegression(max_iter=2000, random_state=42), True),
        "Decision Tree": (DecisionTreeClassifier(max_depth=6, random_state=42), False),
        "Random Forest": (
            RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced"),
            False,
        ),
        "SVM": (SVC(probability=True, kernel="rbf", C=1.0, random_state=42), True),
    }

    comparison_rows: list[dict[str, Any]] = []
    trained_models: dict[str, Any] = {}
    model_test_data: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}

    for name, (model, needs_scaling) in models.items():
        xtr = x_train_scaled if needs_scaling else x_train
        xte = x_test_scaled if needs_scaling else x_test
        scores, y_pred, y_prob = evaluate_model(model, xtr, xte, y_train, y_test)
        comparison_rows.append({"Model": name, **scores})
        trained_models[name] = model
        model_test_data[name] = (np.asarray(y_test), y_pred, y_prob)

    comparison_df = pd.DataFrame(comparison_rows).sort_values(by="ROC-AUC", ascending=False)
    best_model_name = str(comparison_df.iloc[0]["Model"])
    best_model = trained_models[best_model_name]

    joblib.dump(best_model, MODEL_DIR / "model.pkl")
    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
    joblib.dump(trained_models["Random Forest"], MODEL_DIR / "rf_model.pkl")
    comparison_df.to_csv(MODEL_DIR / "model_comparison.csv", index=False)

    feature_stats = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "mean": x.mean().values,
            "std": x.std().replace(0, 1.0).values,
            "median": x.median().values,
        }
    )
    feature_stats.to_csv(MODEL_DIR / "feature_stats.csv", index=False)

    rf = trained_models["Random Forest"]
    rf_importance = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "importance": rf.feature_importances_,
        }
    ).sort_values("importance", ascending=False)
    rf_importance.to_csv(MODEL_DIR / "rf_feature_importance.csv", index=False)

    y_true, y_pred, y_prob = model_test_data[best_model_name]
    conf = confusion_matrix(y_true, y_pred)
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    np.save(MODEL_DIR / "confusion_matrix.npy", conf)
    np.savez(MODEL_DIR / "roc_curve.npz", fpr=fpr, tpr=tpr)

    best_metrics_row = comparison_df.iloc[0].to_dict()
    with open(MODEL_DIR / "best_model_metrics.json", "w", encoding="utf-8") as file:
        json.dump(best_metrics_row, file, indent=2)

    save_correlation_heatmap(df)
    df.describe().to_csv(MODEL_DIR / "dataset_statistics.csv")

    print(f"Training complete. Best model: {best_model_name}")
    print(f"Artifacts saved to: {MODEL_DIR}")


if __name__ == "__main__":
    train()
