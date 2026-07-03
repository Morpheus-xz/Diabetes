"""LLM-powered health assistant with strict medical safety guardrails."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_env() -> None:
    """Load environment variables from common project locations."""
    candidates = [
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "backend" / ".env",
        PROJECT_ROOT / "frontend" / ".env",
        PROJECT_ROOT / ".env.local",
    ]
    for path in candidates:
        if path.exists():
            load_dotenv(path, override=False)


_load_env()

DISCLAIMER_LINE = (
    "Disclaimer: This assistant is for education and awareness only. "
    "It does not diagnose, prescribe treatment, or replace a qualified healthcare professional."
)

SYSTEM_PROMPT = (
    "You are an educational diabetes health assistant for a college social internship project. "
    "You provide safe, clear, non-technical guidance about diabetes awareness, risk factors, "
    "screening, prevention, and how to understand the app's prediction output. "
    "Rules: never diagnose disease; never prescribe medicines, doses, or changes to medication; "
    "never claim certainty; do not replace a clinician; encourage users to consult a qualified "
    "healthcare professional for personal advice; if emergency symptoms are mentioned, urge "
    "immediate medical help. "
    "Response style: be warm but concise, use plain language, avoid fear, and format the answer "
    "with short headings or bullets. When relevant, include practical lifestyle steps around food, "
    "activity, sleep, hydration, monitoring, and follow-up. If prediction context is provided, "
    "explain it as a risk estimate only, not a diagnosis."
)

EMERGENCY_KEYWORDS = (
    "chest pain",
    "shortness of breath",
    "trouble breathing",
    "difficulty breathing",
    "confusion",
    "fainting",
    "passed out",
    "seizure",
    "unconscious",
    "severe dehydration",
    "fruity breath",
    "vomiting",
    "can't keep fluids",
    "cannot keep fluids",
    "very drowsy",
    "diabetic ketoacidosis",
    "dka",
    "blood sugar over 300",
    "glucose over 300",
    "blood sugar above 300",
    "glucose above 300",
    "blood sugar under 54",
    "glucose under 54",
)

MEDICATION_KEYWORDS = (
    "dose",
    "dosage",
    "insulin units",
    "metformin",
    "medicine",
    "medication",
    "tablet",
    "prescribe",
    "stop taking",
    "start taking",
    "increase my",
    "decrease my",
)

GENERAL_HEALTH_TOPICS = (
    "diabetes",
    "glucose",
    "blood sugar",
    "insulin",
    "bmi",
    "weight",
    "diet",
    "exercise",
    "symptom",
    "risk",
    "prevention",
    "type 1",
    "type 2",
    "prediabetes",
    "a1c",
    "hba1c",
    "blood pressure",
    "pregnancy",
    "gestational",
)


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    normalized = re.sub(r"\s+", " ", text.lower())
    return any(keyword in normalized for keyword in keywords)


class HealthAssistant:
    """Provider-agnostic health assistant (Gemini-first, OpenAI optional)."""

    def __init__(self) -> None:
        self.provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.gemini_api_key = (
            os.getenv("GEMINI_API_KEY", "").strip()
            or os.getenv("GOOGLE_API_KEY", "").strip()
            or os.getenv("VITE_GEMINI_API_KEY", "").strip()
        )
        self.gemini_model = os.getenv("GEMINI_MODEL", "").strip()

    def _safe_history(self, history: list[dict[str, str]]) -> list[dict[str, str]]:
        """Keep recent user/assistant turns in the role format LLM providers expect."""
        safe_turns: list[dict[str, str]] = []
        for turn in history[-8:]:
            role = turn.get("role", "").strip().lower()
            content = turn.get("content", "").strip()
            if role in {"user", "assistant"} and content:
                safe_turns.append({"role": role, "content": content[:1200]})
        return safe_turns

    def _history_text(self, history: list[dict[str, str]]) -> str:
        safe_turns = self._safe_history(history)
        if not safe_turns:
            return "No previous messages."
        return "\n".join(f"{turn['role'].title()}: {turn['content']}" for turn in safe_turns)

    def _safety_response(self, user_message: str) -> str | None:
        if _contains_any(user_message, EMERGENCY_KEYWORDS):
            return (
                "This could be urgent. Please seek immediate medical help now, especially if symptoms are severe, "
                "new, or worsening. If you are in the United States, call 911 or your local emergency number.\n\n"
                "While waiting for help, do not drive yourself if you feel faint, confused, very weak, or short of breath. "
                "If you have diabetes supplies and are fully alert, follow the emergency plan previously given by your clinician.\n\n"
                f"{DISCLAIMER_LINE}"
            )

        if _contains_any(user_message, MEDICATION_KEYWORDS):
            return (
                "I cannot recommend medication names, doses, or changes to insulin/tablets. Those decisions depend on your "
                "medical history, lab results, other medicines, and current symptoms.\n\n"
                "What you can do safely:\n"
                "- Contact your doctor, diabetes educator, or pharmacist for personal medication advice.\n"
                "- If you already have a prescribed plan, follow that plan unless a clinician tells you otherwise.\n"
                "- If you feel very unwell, have very high/low glucose readings, vomiting, confusion, or breathing trouble, seek urgent care.\n\n"
                f"{DISCLAIMER_LINE}"
            )

        if not _contains_any(user_message, GENERAL_HEALTH_TOPICS):
            return (
                "I can help with diabetes awareness, risk factors, prevention, screening, lifestyle habits, and explaining this app's "
                "prediction results. Please ask a diabetes or health-risk question, and I will keep the answer practical and easy to understand.\n\n"
                f"{DISCLAIMER_LINE}"
            )

        return None

    def _openai_response(self, prompt: str, history: list[dict[str, str]]) -> str:
        if not self.openai_api_key:
            return (
                "I can explain diabetes concepts and your prediction context, but no API key is configured. "
                "Set OPENAI_API_KEY in your .env file.\n\n"
                + DISCLAIMER_LINE
            )

        from openai import OpenAI

        client = OpenAI(api_key=self.openai_api_key)
        messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self._safe_history(history))
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.3,
        )
        content = completion.choices[0].message.content or ""
        if DISCLAIMER_LINE.lower() not in content.lower():
            content = f"{content.strip()}\n\n{DISCLAIMER_LINE}"
        return content

    def _gemini_response(self, prompt: str, history: list[dict[str, str]]) -> str:
        if not self.gemini_api_key:
            return (
                "Gemini provider selected but no Gemini key was found. "
                "Set GEMINI_API_KEY in one of: .env, backend/.env, or frontend/.env "
                "(or export GEMINI_API_KEY/GOOGLE_API_KEY in your shell), then restart backend.\n\n"
                + DISCLAIMER_LINE
            )
        try:
            from google import genai
            from google.genai import types
        except ImportError as error:
            raise RuntimeError(
                "Gemini client is not installed. Run `pip install -r requirements.txt` to install `google-genai`."
            ) from error

        model_candidates = [
            self.gemini_model,
            "gemini-flash-latest",
            "gemini-3.5-flash",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
        ]
        model_candidates = [model for model in model_candidates if model]

        client = genai.Client(
            api_key=self.gemini_api_key,
            http_options=types.HttpOptions(timeout=20000),
        )
        last_error = ""
        for model_name in model_candidates:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=f"Recent conversation:\n{self._history_text(history)}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        system_instruction=SYSTEM_PROMPT,
                    ),
                )
                text = response.text or ""
                if DISCLAIMER_LINE.lower() not in text.lower():
                    text = f"{text.strip()}\n\n{DISCLAIMER_LINE}"
                return text
            except Exception as error:  # surface a clear final error after trying supported model fallbacks
                last_error = str(error)
                continue

        raise RuntimeError(
            "Gemini request failed for all configured/default models. "
            "Set `GEMINI_MODEL` to a model available for your API key and region "
            "(for example `gemini-3.5-flash` or `gemini-2.5-flash`)."
            + (f" Last error: {last_error}" if last_error else "")
        )

    def ask(
        self,
        user_message: str,
        prediction_context: str | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Generate a safe educational response for diabetes-awareness questions."""
        history = history or []
        safety_answer = self._safety_response(user_message)
        if safety_answer:
            return safety_answer

        context_block = (
            f"\nPrediction context:\n{prediction_context}\n"
            if prediction_context
            else "\nNo current prediction context provided.\n"
        )
        prompt = (
            f"{context_block}\n"
            f"User question: {user_message}\n\n"
            "Write a helpful response using this structure when it fits:\n"
            "1. Short answer\n"
            "2. What it means\n"
            "3. Practical next steps\n"
            "4. When to consult a doctor\n"
            "Keep it under 220 words unless the user asks for detail. Do not repeat the full prediction context."
        )

        if self.provider == "openai":
            return self._openai_response(prompt, history)
        return self._gemini_response(prompt, history)
