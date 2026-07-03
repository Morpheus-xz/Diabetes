import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 30000,
});

export const getHealth = async () => (await api.get("/api/health")).data;
export const predictRisk = async (payload) => (await api.post("/api/predict", payload)).data;
export const askAssistant = async (payload) =>
  (await api.post("/api/chat", payload, { timeout: 90000 })).data;
export const getSummary = async () => (await api.get("/api/analytics/summary")).data;
export const getModelComparison = async () =>
  (await api.get("/api/analytics/model-comparison")).data;
export const getFeatureImportance = async () =>
  (await api.get("/api/analytics/feature-importance")).data;
export const getConfusionMatrix = async () =>
  (await api.get("/api/analytics/confusion-matrix")).data;
export const getRoc = async () => (await api.get("/api/analytics/roc")).data;
export const getHistory = async () => (await api.get("/api/history")).data;
export const getHistoryExportUrl = () =>
  `${import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"}/api/history/export`;
