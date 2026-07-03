# AI-Based Early Diabetes Risk Prediction and Health Assistance System

A production-style **React + FastAPI** web application for early diabetes awareness using machine learning and an AI health assistant.

> **Medical disclaimer:** This project is for educational and awareness purposes only. It does not diagnose or replace professional healthcare.

---

## Project Overview

This system trains on the **PIMA Indians Diabetes Dataset**, compares multiple ML models, selects the best model by **ROC-AUC**, and exposes:

- prediction APIs
- analytics APIs
- chatbot APIs
- a professional React dashboard

---

## Features

- Clean React web UI (responsive, modern, smooth navigation)
- Prediction with probability + risk level (Low/Moderate/High)
- Explainable output using Random Forest feature contribution cues
- Analytics dashboard:
  - model comparison table
  - feature importance
  - ROC curve
  - confusion matrix
  - prediction history
- AI Health Assistant with strict safety instructions:
  - never diagnoses
  - never prescribes medication
  - always includes disclaimer
- Local prediction history + CSV export endpoint

---

## UN SDG Mapping

- **Primary SDG:** Good Health & Well-Being (**SDG 3**)
- Also aligned with:
  - **SDG 9**: Industry, Innovation and Infrastructure
  - **SDG 10**: Reduced Inequalities

---

## Tech Stack

### Frontend
- React
- Vite
- React Router
- Recharts

### Backend
- FastAPI
- Pydantic
- Uvicorn

### ML
- Scikit-learn
- Pandas
- NumPy
- Joblib

### Visualization / Artifacts
- Matplotlib
- Plotly (artifact/data compatibility)

### AI Chatbot
- OpenAI API (default)
- Gemini (optional switch)

---

## Folder Structure

```text
Diabetes-AI/
├── backend/
│   ├── main.py
│   ├── schemas.py
│   └── services/
│       ├── analytics.py
│       ├── chatbot.py
│       ├── history.py
│       └── predictor.py
├── frontend/
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── api.js
│       ├── styles.css
│       ├── components/
│       └── pages/
├── data/
├── model/
│   ├── train_model.py
│   ├── model.pkl
│   └── scaler.pkl
├── predict.py
├── train_model.py
├── requirements.txt
├── .env
└── .gitignore
```

---

## Dataset Setup

Place the PIMA dataset CSV at:

```text
data/diabetes.csv
```

Expected columns:

- Pregnancies
- Glucose
- BloodPressure
- SkinThickness
- Insulin
- BMI
- DiabetesPedigreeFunction
- Age
- Outcome

---

## Installation

### 1. Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Environment Variables

Keep a local `.env` file in the project root. Do not commit real API keys. Set:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key
# Optional fallback:
# OPENAI_API_KEY=your_openai_key
# OPENAI_MODEL=gpt-4o-mini
# Optional Gemini model override:
# GEMINI_MODEL=gemini-2.5-flash
# VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## Train the Model

The trained model files are already expected at `model/model.pkl` and `model/scaler.pkl`. Retrain only if those files are missing or if the dataset changes.

```bash
python model/train_model.py
```

Generates:

- `model/model.pkl`
- `model/scaler.pkl`
- comparison, ROC, confusion matrix, feature importance artifacts

---

## Run the Application

### Terminal 1: Start backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

If your terminal is already inside the `backend` folder, use:

```bash
uvicorn main:app --reload
```

Backend default URL:

```text
http://127.0.0.1:8000
```

### Terminal 2: Start frontend

```bash
cd frontend
npm run dev
```

Frontend default URL:

```text
http://localhost:5173
```

---

## Deployment

### Backend on Render

Use the included `render.yaml` blueprint, or create a Render Web Service manually with:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Render environment variables:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash
```

The Render build runs `python model/train_model.py`, so the deployed backend has both prediction files and analytics artifacts. Keep `data/diabetes.csv` in the repository because training depends on it.

After deployment, verify:

```text
https://your-render-service.onrender.com/api/health
```

Then verify analytics endpoints:

```text
https://your-render-service.onrender.com/api/analytics/summary
https://your-render-service.onrender.com/api/analytics/model-comparison
https://your-render-service.onrender.com/api/analytics/feature-importance
https://your-render-service.onrender.com/api/analytics/confusion-matrix
https://your-render-service.onrender.com/api/analytics/roc
```

### Frontend on Vercel

Deploy the `frontend` directory as the Vercel project.

Vercel settings:

```text
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
```

Vercel environment variable:

```env
VITE_API_BASE_URL=https://your-render-service.onrender.com
```

The backend accepts requests from any frontend origin, so no extra CORS URL update is needed after Vercel deployment.

---

## API Endpoints

- `GET /api/health`
- `POST /api/predict`
- `POST /api/chat`
- `GET /api/analytics/summary`
- `GET /api/analytics/model-comparison`
- `GET /api/analytics/feature-importance`
- `GET /api/analytics/confusion-matrix`
- `GET /api/analytics/roc`
- `GET /api/history`
- `GET /api/history/export`

---

## Future Improvements

- SHAP-based local explanation
- Authentication and user-specific history
- Cloud deployment + CI/CD
- Multi-language assistant
- Enhanced preventive health plans

---

## License

For academic/social internship use. Add your preferred open-source license before public release.

---

## Contributors

- Your Name
- Contributor 2
