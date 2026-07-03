import { NavLink } from "react-router-dom";

const items = [
  { to: "/", label: "Home", icon: "🏠" },
  { to: "/prediction", label: "Prediction", icon: "🧪" },
  { to: "/analytics", label: "Analytics", icon: "📊" },
  { to: "/assistant", label: "AI Health Assistant", icon: "🤖" },
  { to: "/about", label: "About", icon: "ℹ️" },
];

export default function Sidebar({ darkMode, onToggleDark, modelLoaded }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-title">🩺 Diabetes AI</div>
      <p className="sidebar-subtitle">Professional early-risk awareness system</p>
      <button className="toggle-btn" onClick={onToggleDark}>
        {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
      </button>
      <nav className="nav-list">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <span>{item.icon}</span> {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="status-wrap">
        <div className={`status-chip ${modelLoaded ? "ok" : "warn"}`}>
          {modelLoaded ? "Model Ready" : "Model Missing"}
        </div>
      </div>
      <p className="sidebar-note">
        Educational tool only. Always consult qualified healthcare professionals.
      </p>
    </aside>
  );
}

