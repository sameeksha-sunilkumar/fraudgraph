// src/api/index.js — FraudGraph
import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const client = axios.create({ baseURL: BASE_URL });

export const api = {
  // Dashboard
  getDashboardSummary: () => client.get("/dashboard/summary"),
  getRiskChart: () => client.get("/dashboard/risk-chart"),

  // Accounts
  getAccounts: () => client.get("/accounts/"),
  getAccount: (id) => client.get(`/accounts/${id}`),
  getFlaggedAccounts: () => client.get("/accounts/flagged/list"),

  // Transactions
  getTransactions: (limit = 50) => client.get(`/transactions/?limit=${limit}`),
  getFlaggedTransactions: () => client.get("/transactions/flagged"),
  getAccountTransactions: (id) => client.get(`/transactions/account/${id}`),

  // Fraud Cases
  getCases: () => client.get("/cases/"),
  getOpenCases: () => client.get("/cases/open"),
  resolveCase: (id) => client.patch(`/cases/${id}/resolve`),
  markFalsePositive: (id) => client.patch(`/cases/${id}/false-positive`),

  // ── Jac Agent Walkers ──────────────────────────────────────────────────────
  runDetection: (account_id) =>
    client.post("/agent/detect", { account_id }),
  runAnomalies: (account_id, window_hours = 24) =>
    client.post("/agent/anomalies", { account_id, window_hours }),
  runEscalation: (account_id) =>
    client.post("/agent/escalate", { account_id }),
  runSynthesis: () =>
    client.post("/agent/synthesize", {}),
  runFullScan: (account_id) =>
    client.post("/agent/full-scan", { account_id }),
  getAgentLogs: (limit = 20) =>
    client.get(`/agent/logs?limit=${limit}`),
};
