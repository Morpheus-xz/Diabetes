export default function HomePage() {
  return (
    <div>
      <h1 className="page-title">AI-Based Early Diabetes Risk Prediction and Health Assistance System</h1>
      <p className="page-subtitle">
        Production-style web application for early diabetes awareness using machine learning and AI assistance.
      </p>

      <div className="metrics-grid">
        <div className="metric-card">
          <h2>4</h2>
          <p>ML Models Compared</p>
        </div>
        <div className="metric-card">
          <h2>5</h2>
          <p>Core Product Pages</p>
        </div>
        <div className="metric-card">
          <h2>24/7</h2>
          <p>Educational Assistant</p>
        </div>
      </div>

      <div className="card">
        <h3>Features</h3>
        <p>
          Risk prediction with probability, model comparison, explainable output, professional analytics,
          educational chatbot, PDF report support, and prediction history export.
        </p>
      </div>

      <div className="two-col">
        <div className="card">
          <h3>Technology Stack</h3>
          <p>React, FastAPI, Python, Scikit-learn, Pandas, NumPy, Plotly-compatible analytics data, OpenAI API.</p>
        </div>
        <div className="card">
          <h3>UN SDG Mapping</h3>
          <p>
            <strong>Primary:</strong> SDG 3 (Good Health & Well-Being)
            <br />
            <strong>Also:</strong> SDG 9 and SDG 10
          </p>
        </div>
      </div>
    </div>
  );
}

