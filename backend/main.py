"""
main.py — FraudGraph
FastAPI application: fraud detection API powered by Jac agentic walkers.
Adapted from FinFlow360's main.py.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import accounts, transactions, fraud_cases, agent, dashboard

app = FastAPI(
    title="FraudGraph API",
    description="Real-Time Agentic Fraud Detection Engine — powered by Jac walkers",
    version="1.0.0",
)

# CORS — allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://fraudgraph.vercel.app",
        "https://fraudgraph-three.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(fraud_cases.router)
app.include_router(agent.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {
        "app": "FraudGraph",
        "description": "Agentic Fraud Detection Engine powered by Jac walkers",
        "version": "1.0.0",
        "jac_walkers": [
            "FraudDetectionWalker",
            "AnomalyPatternWalker",
            "EscalationWalker",
            "SynthesisWalker",
        ],
        "docs": "/docs",
    }
