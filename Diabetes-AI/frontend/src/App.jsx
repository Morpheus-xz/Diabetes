import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { getHealth } from "./api";
import Sidebar from "./components/Sidebar";
import AboutPage from "./pages/AboutPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import AssistantPage from "./pages/AssistantPage";
import HomePage from "./pages/HomePage";
import PredictionPage from "./pages/PredictionPage";

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [modelLoaded, setModelLoaded] = useState(false);
  const [predictionContext, setPredictionContext] = useState(null);

  useEffect(() => {
    getHealth()
      .then((data) => setModelLoaded(Boolean(data.model_loaded)))
      .catch(() => setModelLoaded(false));
  }, []);

  useEffect(() => {
    document.body.className = darkMode ? "theme-dark" : "theme-light";
  }, [darkMode]);

  return (
    <div className="layout">
      <Sidebar darkMode={darkMode} onToggleDark={() => setDarkMode((prev) => !prev)} modelLoaded={modelLoaded} />
      <main className="content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route
            path="/prediction"
            element={<PredictionPage onPredictionUpdate={(ctx) => setPredictionContext(ctx)} />}
          />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/assistant" element={<AssistantPage predictionContext={predictionContext} />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

