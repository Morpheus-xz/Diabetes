import { useState } from "react";
import { predictRisk } from "../api";
import RiskGauge from "../components/RiskGauge";

const initialForm = {
  Pregnancies: 1,
  Glucose: 120,
  BloodPressure: 70,
  SkinThickness: 20,
  Insulin: 79,
  BMI: 28,
  DiabetesPedigreeFunction: 0.47,
  Age: 33,
};

export default function PredictionPage({ onPredictionUpdate }) {
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const onChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: Number(value) }));
  };

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await predictRisk(form);
      setResult(data);
      const context = `Prediction: ${data.risk_level}
Probability: ${data.probability_percent}%
Glucose: ${form.Glucose}
BMI: ${form.BMI}
Age: ${form.Age}
BloodPressure: ${form.BloodPressure}
Insulin: ${form.Insulin}
Pregnancies: ${form.Pregnancies}
DiabetesPedigreeFunction: ${form.DiabetesPedigreeFunction}`;
      onPredictionUpdate?.(context);
    } catch (err) {
      setError(err?.response?.data?.detail || "Prediction failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
  ];

  return (
    <div>
      <h1 className="page-title">Prediction</h1>
      <p className="page-subtitle">
        Enter health values and generate a diabetes risk estimate with plain-language explanation.
      </p>
      <div className="disclaimer">
        This application is intended for educational and awareness purposes only. It is not a substitute for
        professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider
        regarding your health.
      </div>
      <form className="card" onSubmit={submit}>
        <div className="form-grid">
          {fields.map((field) => (
            <label key={field} className="input-group">
              <span>{field}</span>
              <input
                type="number"
                value={form[field]}
                step={field === "BMI" || field === "DiabetesPedigreeFunction" ? "0.01" : "1"}
                onChange={(e) => onChange(field, e.target.value)}
                required
              />
            </label>
          ))}
        </div>
        <button className="primary-btn" type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Predict Risk"}
        </button>
      </form>

      {error && <div className="error-box">{error}</div>}

      {result && (
        <div className="two-col">
          <div className="card risk-card">
            <h3>
              Risk Level:{" "}
              <span
                className={
                  result.risk_level === "Low"
                    ? "tag low"
                    : result.risk_level === "Moderate"
                    ? "tag moderate"
                    : "tag high"
                }
              >
                {result.risk_level}
              </span>
            </h3>
            <p>
              <strong>Probability:</strong> {result.probability_percent}%
            </p>
            <p>{result.explanation}</p>
          </div>
          <RiskGauge probability={result.probability_percent} />
        </div>
      )}
    </div>
  );
}

