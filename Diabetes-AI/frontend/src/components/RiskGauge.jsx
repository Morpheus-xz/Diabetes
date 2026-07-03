export default function RiskGauge({ probability }) {
  const value = Math.max(0, Math.min(100, Number(probability || 0)));
  const color = value < 35 ? "#2e7d32" : value < 65 ? "#f9a825" : "#c62828";
  return (
    <div className="gauge-card">
      <div className="gauge-label">Predicted Diabetes Risk</div>
      <div className="gauge-number">{value.toFixed(2)}%</div>
      <div className="gauge-track">
        <div className="gauge-fill" style={{ width: `${value}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}

