"""
routers/agent.py — FraudGraph
Exposes Jac walker execution as REST endpoints.
This is the agentic core of FraudGraph.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import time
from jac_runner import (
    run_fraud_detection,
    run_anomaly_patterns,
    run_escalation,
    run_synthesis,
)
from database import SessionLocal, AgentScanLog
import json

router = APIRouter(prefix="/agent", tags=["Jac Agent Walkers"])


class ScanRequest(BaseModel):
    account_id: str
    window_hours: Optional[int] = 24


class SynthesisRequest(BaseModel):
    scan_id: Optional[str] = None


def _log_scan(walker: str, account_id: Optional[str], result: dict, duration_ms: int):
    db = SessionLocal()
    scan_id = "SCAN-" + str(uuid.uuid4())[:8].upper()
    db.add(AgentScanLog(
        scan_id=scan_id,
        walker_name=walker,
        account_id=account_id,
        result_summary=json.dumps(result)[:500],
        duration_ms=duration_ms,
    ))
    db.commit()
    db.close()
    return scan_id


# ─────────────────────────────────────────────
# POST /agent/detect
# Run FraudDetectionWalker on an account
# ─────────────────────────────────────────────
@router.post("/detect")
def detect_fraud(req: ScanRequest):
    """
    Launches the FraudDetectionWalker Jac walker.
    Traverses account → transaction nodes, ML-scores each tx,
    computes account-level fraud score and risk tier.
    """
    start = time.time()
    result = run_fraud_detection(req.account_id)
    duration = int((time.time() - start) * 1000)
    _log_scan("FraudDetectionWalker", req.account_id, result, duration)
    return {
        "walker": "FraudDetectionWalker",
        "duration_ms": duration,
        "result": result,
    }


# ─────────────────────────────────────────────
# POST /agent/anomalies
# Run AnomalyPatternWalker on an account
# ─────────────────────────────────────────────
@router.post("/anomalies")
def detect_anomalies(req: ScanRequest):
    """
    Launches the AnomalyPatternWalker Jac walker.
    Detects velocity spikes, geo anomalies, and high-risk merchant clusters.
    """
    start = time.time()
    result = run_anomaly_patterns(req.account_id, req.window_hours)
    duration = int((time.time() - start) * 1000)
    _log_scan("AnomalyPatternWalker", req.account_id, result, duration)
    return {
        "walker": "AnomalyPatternWalker",
        "duration_ms": duration,
        "result": result,
    }


# ─────────────────────────────────────────────
# POST /agent/escalate
# Run EscalationWalker — uses by llm() for action recommendation
# ─────────────────────────────────────────────
@router.post("/escalate")
def escalate_account(req: ScanRequest):
    """
    Launches the EscalationWalker Jac walker.
    Uses by llm() to recommend the correct action (block, freeze, verify, etc.)
    Creates FraudCaseNodes for high/critical accounts.
    """
    start = time.time()
    result = run_escalation(req.account_id)
    duration = int((time.time() - start) * 1000)
    _log_scan("EscalationWalker", req.account_id, result, duration)
    return {
        "walker": "EscalationWalker",
        "duration_ms": duration,
        "result": result,
    }


# ─────────────────────────────────────────────
# POST /agent/synthesize
# Run SynthesisWalker — LLM produces executive fraud report
# ─────────────────────────────────────────────
@router.post("/synthesize")
def synthesize_report(req: SynthesisRequest):
    """
    Launches the SynthesisWalker Jac walker.
    Traverses all flagged accounts, produces an AI executive fraud report
    using by llm() — the full multi-agent orchestration finale.
    """
    scan_id = req.scan_id or "SCAN-" + str(uuid.uuid4())[:8].upper()
    start = time.time()
    result = run_synthesis(scan_id)
    duration = int((time.time() - start) * 1000)
    _log_scan("SynthesisWalker", None, result, duration)
    return {
        "walker": "SynthesisWalker",
        "scan_id": scan_id,
        "duration_ms": duration,
        "result": result,
    }


# ─────────────────────────────────────────────
# POST /agent/full-scan
# Orchestrates all 4 walkers sequentially for one account
# ─────────────────────────────────────────────
@router.post("/full-scan")
def full_agent_scan(req: ScanRequest):
    """
    Full multi-walker agent pipeline for one account:
    1. FraudDetectionWalker  → score all transactions
    2. AnomalyPatternWalker  → detect patterns
    3. EscalationWalker      → create case + LLM action
    4. SynthesisWalker       → executive report
    """
    start = time.time()

    detection = run_fraud_detection(req.account_id)
    anomalies = run_anomaly_patterns(req.account_id, req.window_hours)
    escalation = run_escalation(req.account_id)
    scan_id = "SCAN-" + str(uuid.uuid4())[:8].upper()
    synthesis = run_synthesis(scan_id)

    total_duration = int((time.time() - start) * 1000)

    return {
        "pipeline": "full_agent_scan",
        "account_id": req.account_id,
        "total_duration_ms": total_duration,
        "walkers_executed": [
            "FraudDetectionWalker",
            "AnomalyPatternWalker",
            "EscalationWalker",
            "SynthesisWalker",
        ],
        "results": {
            "detection": detection,
            "anomalies": anomalies,
            "escalation": escalation,
            "synthesis": synthesis,
        },
    }


# ─────────────────────────────────────────────
# GET /agent/logs
# Recent walker execution audit trail
# ─────────────────────────────────────────────
@router.get("/logs")
def get_agent_logs(limit: int = 20):
    db = SessionLocal()
    logs = (
        db.query(AgentScanLog)
        .order_by(AgentScanLog.created_at.desc())
        .limit(limit)
        .all()
    )
    db.close()
    return [
        {
            "scan_id": l.scan_id,
            "walker": l.walker_name,
            "account_id": l.account_id,
            "duration_ms": l.duration_ms,
            "created_at": str(l.created_at),
        }
        for l in logs
    ]
