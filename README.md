# FraudGraph — Agentic Fraud Detection Engine

> Real-time fraud detection powered by **Jac walkers** traversing a live transaction graph.
> Think of it as **four AI agents working together** to find, analyze, escalate, and report fraud — autonomously.

---

## 🤖 What Makes This Agentic (Jac/Jaseci Features Used)

FraudGraph is built around **four Jac walkers** that traverse a fraud knowledge graph using **Object Spatial Programming**:

| Walker | What it does | Jac Feature |
|--------|-------------|-------------|
| `FraudDetectionWalker` | Traverses account→transaction nodes, ML-scores each tx | Walker traversal, node state mutation |
| `AnomalyPatternWalker` | Detects velocity spikes, geo anomalies, merchant risk clusters | Graph pattern matching, edge traversal |
| `EscalationWalker` | Routes high-risk accounts, decides action via AI | **`by llm()`** — LLM decides block/freeze/verify |
| `SynthesisWalker` | Aggregates all findings, writes executive report | **`by llm()`** — LLM produces structured report |

This is **not** a UI wrapper around an API call. The walkers genuinely traverse the graph, collect evidence across nodes, and make decisions — including using `by llm()` for actions that require judgment.

---

## 🧠 How It Works

```
Account Node ──has_transaction──► Transaction Node (×N)
                                         │
                              FraudDetectionWalker visits each
                              → ML scores each transaction
                              → Flags high-probability fraud
                                         │
                              AnomalyPatternWalker overlays
                              → Velocity detection
                              → Geo anomaly (cross-border)
                              → High-risk merchant clusters
                                         │
                              EscalationWalker evaluates
                              → by llm() recommends action
                              → Creates FraudCaseNode
                              → Assigns to human/auto review
                                         │
                              SynthesisWalker aggregates
                              → by llm() writes executive report
                              → Top patterns, immediate actions
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Agentic Core** | **Jac / Jaseci** (walkers, nodes, `by llm()`) |
| Backend | Python FastAPI |
| ML Scoring | Scikit-learn (Isolation Forest) |
| Database | SQLite + SQLAlchemy |
| Frontend | React + Tailwind CSS + Recharts |
| Deployment | Render (backend) + Vercel (frontend) |

---

## 🚀 Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- `pip install jaclang` (for Jac walker execution)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
python seed_data.py
uvicorn main:app --reload
```

Backend: http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/docs

> **Note:** If `jaclang` is not installed, the app runs in **simulation mode** — the walker
> outputs are realistically simulated so the full UI and pipeline demo works without Jac CLI.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

---

## 📁 Project Structure

```
fraudgraph/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── database.py                # SQLAlchemy models
│   ├── seed_data.py               # Realistic fraud scenario data
│   ├── fraud_tools.py             # ML tools called by Jac walkers
│   ├── jac_runner.py              # Python ↔ Jac bridge
│   ├── jac/
│   │   └── fraud_agent.jac        # ★ ALL FOUR JAC WALKERS ★
│   └── routers/
│       ├── agent.py               # /agent/* — walker endpoints
│       ├── accounts.py
│       ├── transactions.py
│       ├── fraud_cases.py
│       └── dashboard.py
└── frontend/
    └── src/
        ├── components/
        │   ├── FraudScore.jsx      # Risk score panel
        │   ├── AgentPanel.jsx      # ★ Live walker execution UI ★
        │   ├── RiskChart.jsx       # Account scatter plot
        │   ├── TransactionFeed.jsx # Live transaction table
        │   └── FraudCases.jsx      # Open cases + resolve/FP
        ├── pages/
        │   └── Dashboard.jsx
        └── api/
            └── index.js
```

---

## 🔌 Agent API Endpoints

| Endpoint | Walker | Description |
|----------|--------|-------------|
| `POST /agent/detect` | `FraudDetectionWalker` | Score all transactions for an account |
| `POST /agent/anomalies` | `AnomalyPatternWalker` | Detect velocity/geo/merchant patterns |
| `POST /agent/escalate` | `EscalationWalker` | Create case + LLM action recommendation |
| `POST /agent/synthesize` | `SynthesisWalker` | Executive fraud report via `by llm()` |
| `POST /agent/full-scan` | All 4 walkers | Full multi-agent pipeline for one account |
| `GET /agent/logs` | — | Walker execution audit trail |

---

## 👥 Team

Built for **JacHacks 2026**
Track: **Agentic AI (Flagship)**
