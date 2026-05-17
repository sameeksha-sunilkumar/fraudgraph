"""
jac_runner.py
Python bridge between FastAPI and the Jac fraud agent.
Executes walkers and returns structured results.
"""

import subprocess
import json
import os
from typing import Optional

JAC_FILE = os.path.join(os.path.dirname(__file__), "jac", "fraud_agent.jac")


def _run_jac(walker: str, payload: dict) -> dict:
    """
    Execute a Jac walker via the jaclang CLI and capture the report output.
    Falls back to simulation mode if jaclang is not installed.
    """
    try:
        input_json = json.dumps(payload)
        result = subprocess.run(
            ["jac", "run", JAC_FILE, "--walker", walker, "--input", input_json],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            # jaclang error — fall back to simulation
            return _simulate_walker(walker, payload)
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return _simulate_walker(walker, payload)


def _simulate_walker(walker: str, payload: dict) -> dict:
    """
    Simulation mode: mirrors what the Jac walker would return.
    Used for demo/testing when jaclang CLI is not available.
    """
    import random
    import hashlib

    account_id = payload.get("account_id", "unknown")
    seed = int(hashlib.md5(account_id.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    if walker == "FraudDetectionWalker":
        fraud_score = rng.uniform(5, 95)
        risk_tier = (
            "critical" if fraud_score > 75 else
            "high" if fraud_score > 50 else
            "medium" if fraud_score > 25 else
            "low"
        )
        flagged = []
        tx_count = rng.randint(3, 15)
        for i in range(tx_count):
            prob = rng.uniform(0, 1)
            if prob > 0.6:
                flagged.append({
                    "tx_id": f"TX-{account_id}-{i:03d}",
                    "amount": round(rng.uniform(100, 50000), 2),
                    "merchant": rng.choice(["QuickPay", "GlobalStore", "CryptoExch", "FastMart"]),
                    "fraud_probability": round(prob, 3),
                    "reasons": rng.sample(
                        ["unusual_amount", "geo_anomaly", "velocity_spike",
                         "high_risk_merchant", "odd_hours", "device_mismatch"],
                        k=rng.randint(1, 3),
                    ),
                })
        return {
            "account_id": account_id,
            "fraud_score": round(fraud_score, 2),
            "risk_tier": risk_tier,
            "flagged_transactions": flagged,
            "tx_scanned": tx_count,
        }

    elif walker == "AnomalyPatternWalker":
        patterns = []
        pattern_types = [
            {"pattern": "velocity_anomaly", "severity": "high",
             "detail": "12 transactions in 2 hours — 4x above baseline"},
            {"pattern": "geo_anomaly", "severity": "high",
             "detail": "Transaction in Nigeria; account home country is India"},
            {"pattern": "high_risk_merchant", "severity": "medium",
             "merchant": "CryptoExch", "merchant_risk": 0.82},
        ]
        count = rng.randint(0, 3)
        patterns = rng.sample(pattern_types, k=count)
        return {
            "account_id": account_id,
            "patterns": patterns,
            "pattern_count": len(patterns),
        }

    elif walker == "EscalationWalker":
        case_id = f"CASE-{account_id}-{rng.randint(10000, 99999)}"
        return {
            "escalated_cases": [case_id],
            "count": 1,
        }

    elif walker == "SynthesisWalker":
        return {
            "summary": (
                "Fraud scan detected elevated risk across multiple accounts. "
                "Velocity attacks and cross-border anomalies are the dominant patterns. "
                "Immediate review of critical-tier accounts is recommended."
            ),
            "critical_count": rng.randint(1, 5),
            "high_count": rng.randint(3, 10),
            "top_patterns": [
                "Velocity spike attacks (>10 tx/hour)",
                "Geographic anomalies (cross-border in <1hr)",
                "High-risk merchant clustering",
            ],
            "immediate_actions": [
                "Block all critical-tier accounts pending review",
                "Send SMS verification to high-tier accounts",
                "Escalate 3 cases to fraud analyst team",
            ],
        }

    return {"error": f"Unknown walker: {walker}"}


# ── Public API ────────────────────────────────────────────────────────────────

def run_fraud_detection(account_id: str) -> dict:
    return _run_jac("FraudDetectionWalker", {"account_id": account_id})


def run_anomaly_patterns(account_id: str, window_hours: int = 24) -> dict:
    return _run_jac("AnomalyPatternWalker", {
        "account_id": account_id,
        "recent_tx_window": window_hours,
    })


def run_escalation(account_id: str) -> dict:
    return _run_jac("EscalationWalker", {"account_id": account_id})


def run_synthesis(scan_id: str) -> dict:
    return _run_jac("SynthesisWalker", {"scan_id": scan_id})
