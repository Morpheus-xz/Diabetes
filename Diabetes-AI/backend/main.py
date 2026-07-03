"""FastAPI backend for diabetes prediction, analytics, and chatbot."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

try:
    from backend.schemas import ChatRequest, ChatResponse, HealthInput, PredictionResponse
    from backend.services.analytics import AnalyticsService
    from backend.services.chatbot import DISCLAIMER_LINE, HealthAssistant
    from backend.services.history import HistoryService
    from backend.services.predictor import DiabetesPredictor
except ModuleNotFoundError:
    from schemas import ChatRequest, ChatResponse, HealthInput, PredictionResponse
    from services.analytics import AnalyticsService
    from services.chatbot import DISCLAIMER_LINE, HealthAssistant
    from services.history import HistoryService
    from services.predictor import DiabetesPredictor

app = FastAPI(
    title="Diabetes AI API",
    version="1.0.0",
    description="API for early diabetes risk prediction and educational health assistance.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = DiabetesPredictor()
assistant = HealthAssistant()
analytics = AnalyticsService()
history = HistoryService()


@app.get("/api/health")
def health() -> dict[str, bool]:
    """Basic API health endpoint."""
    return {"ok": True, "model_loaded": predictor.is_loaded}


@app.post("/api/predict", response_model=PredictionResponse)
def predict(payload: HealthInput) -> PredictionResponse:
    """Return diabetes risk prediction and explanation."""
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=400,
            detail=(
                "Model artifacts are missing. Place dataset in data/diabetes.csv "
                "and run python model/train_model.py."
            ),
        )
    result = predictor.predict(payload.model_dump())
    response = PredictionResponse(
        risk_level=result.risk_level,
        probability=result.probability,
        probability_percent=round(result.probability * 100, 2),
        prediction=result.prediction,
        explanation=result.explanation,
        top_contributors=result.top_contributors,
        disclaimer=(
            "This application is intended for educational and awareness purposes only. "
            "It is not a substitute for professional medical advice, diagnosis, or treatment. "
            "Always consult a qualified healthcare provider regarding your health."
        ),
    )
    history.save(
        {
            **payload.model_dump(),
            "probability_percent": response.probability_percent,
            "risk_level": response.risk_level,
            "explanation": response.explanation,
        }
    )
    return response


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Return educational chatbot response."""
    try:
        answer = assistant.ask(
            user_message=payload.message,
            prediction_context=payload.prediction_context,
            history=payload.history,
        )
    except Exception as error:
        answer = (
            f"Unable to fetch Gemini response right now: {error}\n\n"
            f"{DISCLAIMER_LINE}"
        )
    if DISCLAIMER_LINE.lower() not in answer.lower():
        answer = f"{answer}\n\n{DISCLAIMER_LINE}"
    return ChatResponse(response=answer)


@app.get("/api/analytics/summary")
def analytics_summary() -> dict:
    """Return dataset summary and best model metrics."""
    return {
        "dataset": analytics.dataset_summary(),
        "best_model_metrics": analytics.best_model_metrics(),
    }


@app.get("/api/analytics/model-comparison")
def analytics_model_comparison() -> dict:
    """Return model comparison rows."""
    return {"rows": analytics.model_comparison()}


@app.get("/api/analytics/feature-importance")
def analytics_feature_importance() -> dict:
    """Return random forest feature importance."""
    return {"rows": analytics.feature_importance()}


@app.get("/api/analytics/confusion-matrix")
def analytics_confusion_matrix() -> dict:
    """Return confusion matrix."""
    return {"matrix": analytics.confusion_matrix()}


@app.get("/api/analytics/roc")
def analytics_roc() -> dict:
    """Return ROC curve points."""
    return analytics.roc_curve()


@app.get("/api/history")
def get_history() -> dict:
    """Return prediction history rows."""
    return {"rows": history.list()}


@app.get("/api/history/export", response_class=PlainTextResponse)
def export_history() -> str:
    """Export prediction history as CSV text."""
    return history.export_csv()
