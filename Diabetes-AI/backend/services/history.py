"""Prediction history persistence utilities."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


class HistoryService:
    """Store and retrieve prediction history in local CSV."""

    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or Path(__file__).resolve().parents[2]
        self.path = self.root_dir / "data" / "prediction_history.csv"

    def save(self, entry: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": datetime.now().isoformat(timespec="seconds"), **entry}
        df = pd.DataFrame([row])
        if self.path.exists():
            df.to_csv(self.path, mode="a", index=False, header=False)
        else:
            df.to_csv(self.path, index=False)

    def list(self, limit: int = 200) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        df = pd.read_csv(self.path).tail(limit)
        return df.to_dict(orient="records")

    def export_csv(self) -> str:
        if not self.path.exists():
            return "timestamp\n"
        return self.path.read_text(encoding="utf-8")

