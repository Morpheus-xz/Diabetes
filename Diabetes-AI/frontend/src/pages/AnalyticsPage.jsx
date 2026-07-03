import { useEffect, useMemo, useState } from "react";
import {
  getConfusionMatrix,
  getFeatureImportance,
  getHistory,
  getHistoryExportUrl,
  getModelComparison,
  getRoc,
  getSummary,
} from "../api";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Bar,
  BarChart,
} from "recharts";

export default function AnalyticsPage() {
  const [summary, setSummary] = useState(null);
  const [comparison, setComparison] = useState([]);
  const [importance, setImportance] = useState([]);
  const [confusion, setConfusion] = useState([]);
  const [roc, setRoc] = useState({ fpr: [], tpr: [] });
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError("");
      try {
        const [s, c, fi, cm, rc, h] = await Promise.all([
          getSummary(),
          getModelComparison(),
          getFeatureImportance(),
          getConfusionMatrix(),
          getRoc(),
          getHistory(),
        ]);
        setSummary(s);
        setComparison(c.rows || []);
        setImportance(fi.rows || []);
        setConfusion(cm.matrix || []);
        setRoc(rc || { fpr: [], tpr: [] });
        setHistory(h.rows || []);
      } catch (requestError) {
        setError(
          requestError?.response?.data?.detail ||
            "Analytics data could not be loaded. Check that the backend URL is correct and the analytics artifacts exist on the deployed backend."
        );
      } finally {
        setLoading(false);
      }
    };
    run();
  }, []);

  const rocData = useMemo(
    () => (roc.fpr || []).map((fpr, i) => ({ fpr, tpr: roc.tpr?.[i] || 0 })),
    [roc]
  );

  return (
    <div>
      <h1 className="page-title">Analytics</h1>
      <p className="page-subtitle">Interactive model and dataset insights in one view.</p>

      {loading && <div className="disclaimer">Loading analytics...</div>}
      {error && <div className="error-box">{error}</div>}
      {!loading && !error && summary?.dataset?.available === false && (
        <div className="error-box">
          Dataset analytics are unavailable because <strong>data/diabetes.csv</strong> is missing on the backend.
        </div>
      )}

      <div className="metrics-grid">
        <div className="metric-card">
          <h2>{summary?.dataset?.records || "-"}</h2>
          <p>Total Records</p>
        </div>
        <div className="metric-card">
          <h2>{summary?.dataset?.positive_cases || "-"}</h2>
          <p>Positive Cases</p>
        </div>
        <div className="metric-card">
          <h2>{summary?.dataset?.avg_glucose?.toFixed?.(1) || "-"}</h2>
          <p>Average Glucose</p>
        </div>
      </div>

      <div className="card">
        <h3>Model Comparison</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Model</th>
                <th>Accuracy</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1</th>
                <th>ROC-AUC</th>
              </tr>
            </thead>
            <tbody>
              {comparison.map((row) => (
                <tr key={row.Model}>
                  <td>{row.Model}</td>
                  <td>{Number(row.Accuracy).toFixed(3)}</td>
                  <td>{Number(row.Precision).toFixed(3)}</td>
                  <td>{Number(row.Recall).toFixed(3)}</td>
                  <td>{Number(row["F1 Score"]).toFixed(3)}</td>
                  <td>{Number(row["ROC-AUC"]).toFixed(3)}</td>
                </tr>
              ))}
              {!comparison.length && (
                <tr>
                  <td colSpan="6">No model comparison data available. Redeploy the backend after generating model artifacts.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="two-col">
        <div className="card">
          <h3>Feature Importance (Random Forest)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={importance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="feature" tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="importance" fill="#2563eb" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>ROC Curve (Best Model)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={rocData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="fpr" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line dataKey="tpr" stroke="#0ea5e9" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3>Confusion Matrix</h3>
        <div className="matrix-grid">
          <div className="matrix-cell">Pred 0 / Actual 0: {confusion?.[0]?.[0] ?? "-"}</div>
          <div className="matrix-cell">Pred 1 / Actual 0: {confusion?.[0]?.[1] ?? "-"}</div>
          <div className="matrix-cell">Pred 0 / Actual 1: {confusion?.[1]?.[0] ?? "-"}</div>
          <div className="matrix-cell">Pred 1 / Actual 1: {confusion?.[1]?.[1] ?? "-"}</div>
        </div>
      </div>

      <div className="card">
        <div className="row-between">
          <h3>Prediction History</h3>
          <a className="link-btn" href={getHistoryExportUrl()} target="_blank" rel="noreferrer">
            Export CSV
          </a>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Risk</th>
                <th>Probability %</th>
                <th>Glucose</th>
                <th>BMI</th>
                <th>Age</th>
              </tr>
            </thead>
            <tbody>
              {history.slice(-100).reverse().map((row, index) => (
                <tr key={`${row.timestamp}-${index}`}>
                  <td>{row.timestamp}</td>
                  <td>{row.risk_level}</td>
                  <td>{row.probability_percent}</td>
                  <td>{row.Glucose}</td>
                  <td>{row.BMI}</td>
                  <td>{row.Age}</td>
                </tr>
              ))}
              {!history.length && (
                <tr>
                  <td colSpan="6">No prediction history yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
