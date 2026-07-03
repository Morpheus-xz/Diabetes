"""CLI utility to run a diabetes risk prediction from terminal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.services.predictor import DiabetesPredictor, FEATURE_COLUMNS


def build_parser() -> argparse.ArgumentParser:
    """Create command-line parser."""
    parser = argparse.ArgumentParser(description="Predict diabetes risk from clinical features.")
    for feature in FEATURE_COLUMNS:
        parser.add_argument(f"--{feature}", type=float, required=True, help=f"Value for {feature}")
    return parser


def main() -> None:
    """Run prediction and print JSON result."""
    parser = build_parser()
    args = parser.parse_args()
    payload = {feature: getattr(args, feature) for feature in FEATURE_COLUMNS}

    predictor = DiabetesPredictor(root_dir=Path(__file__).resolve().parent)
    result = predictor.predict(payload)

    output = {
        "risk_level": result.risk_level,
        "probability_percent": round(result.probability * 100, 2),
        "prediction": result.prediction,
        "explanation": result.explanation,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
