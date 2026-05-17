"""
fraud_tools.py
Python ML tools imported by the Jac fraud agent.
These are the 'tool use' layer — called from Jac walkers via import:py.
"""

import numpy as np
import random
import hashlib
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

# ── In-memory account baseline store (replaces DB calls for Jac tool use) ──
_account_baselines: dict = {}
_merchant_risk_cache: dict = {}


def _seed_from_string(s: str) -> random.Random:
    seed = int(hashlib.md5(s.encode()).hexdigest()[:8], 16)
    return random.Random(seed)


# ─────────────────────────────────────────────
# TOOL 1: score_transaction
# ML-based fraud probability for a single transaction
# ─────────────────────────────────────────────

def score_transaction(tx: dict) -> dict:
    """
    Returns a fraud probability (0-1) and list of anomaly reasons for a tx.
    Uses rule-based heuristics + Isolation Forest anomaly scoring.
    """
    rng = _seed_from_string(tx.get("tx_id", "default"))
    reasons = []
    risk_factors = []

    amount = tx.get("amount", 0)
    merchant_cat = tx.get("merchant_category", "").lower()
    country = tx.get("country", "IN")
    timestamp = tx.get("timestamp", "")

    # Rule 1: Large round-number amounts
    if amount > 10000 and amount % 1000 == 0:
        reasons.append("large_round_amount")
        risk_factors.append(0.3)

    # Rule 2: High-risk merchant categories
    high_risk_cats = ["crypto", "gambling", "wire_transfer", "jewelry", "electronics"]
    if any(cat in merchant_cat for cat in high_risk_cats):
        reasons.append("high_risk_merchant_category")
        risk_factors.append(0.35)

    # Rule 3: Unusual transaction hour (midnight to 5am)
    try:
        dt = datetime.fromisoformat(timestamp)
        if dt.hour < 5:
            reasons.append("unusual_hour_transaction")
            risk_factors.append(0.2)
    except Exception:
        pass

    # Rule 4: Cross-border transaction flag
    if country not in ["IN", "US", "GB", "SG", "AE"]:
        reasons.append("unusual_transaction_country")
        risk_factors.append(0.25)

    # Rule 5: Very high amount
    if amount > 100000:
        reasons.append("very_high_amount")
        risk_factors.append(0.4)

    # Isolation Forest component (simulated feature vector)
    features = np.array([[
        amount / 100000,
        len(reasons) / 5,
        1.0 if country not in ["IN", "US", "GB"] else 0.0,
        rng.uniform(0, 0.3),  # simulated device risk score
    ]])

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    clf = IsolationForest(contamination=0.1, random_state=42)
    clf.fit(features_scaled)
    anomaly_score = -clf.score_samples(features_scaled)[0]  # higher = more anomalous

    # Combine rule scores + anomaly score
    base_score = sum(risk_factors)
    combined = min(base_score + anomaly_score * 0.3, 1.0)

    return {
        "fraud_probability": round(combined, 4),
        "reasons": reasons,
        "anomaly_score": round(float(anomaly_score), 4),
    }


# ─────────────────────────────────────────────
# TOOL 2: detect_velocity_anomaly
# Checks if tx count in window exceeds account baseline
# ─────────────────────────────────────────────

def detect_velocity_anomaly(account_id: str, tx_count: int, window_hours: int = 24) -> dict:
    """
    Detects if the transaction velocity for an account is anomalous
    compared to its historical baseline.
    """
    rng = _seed_from_string(account_id)
    baseline = _account_baselines.get(account_id, rng.randint(2, 6))

    threshold = baseline * 2.5
    is_anomaly = tx_count > threshold

    severity = "low"
    if tx_count > baseline * 5:
        severity = "critical"
    elif tx_count > baseline * 3:
        severity = "high"
    elif is_anomaly:
        severity = "medium"

    return {
        "is_anomaly": is_anomaly,
        "severity": severity,
        "detail": (
            f"{tx_count} transactions in {window_hours}h — "
            f"{round(tx_count / max(baseline, 1), 1)}x above baseline of {baseline}"
        ) if is_anomaly else f"Normal velocity: {tx_count} tx in {window_hours}h",
        "baseline": baseline,
        "observed": tx_count,
    }


# ─────────────────────────────────────────────
# TOOL 3: get_merchant_risk
# Returns historical fraud rate for a merchant/category
# ─────────────────────────────────────────────

def get_merchant_risk(merchant: str, category: str) -> dict:
    """
    Returns risk score for a merchant based on category and name heuristics.
    """
    cache_key = f"{merchant}::{category}"
    if cache_key in _merchant_risk_cache:
        return _merchant_risk_cache[cache_key]

    rng = _seed_from_string(cache_key)
    cat = category.lower()

    # Base risk by category
    category_risk = {
        "crypto": 0.85,
        "gambling": 0.80,
        "wire_transfer": 0.75,
        "jewelry": 0.60,
        "electronics": 0.50,
        "travel": 0.35,
        "food": 0.10,
        "grocery": 0.05,
        "utilities": 0.05,
    }

    base = 0.2
    for key, val in category_risk.items():
        if key in cat:
            base = val
            break

    # Add merchant-level noise
    noise = rng.uniform(-0.1, 0.1)
    risk_score = round(min(max(base + noise, 0.0), 1.0), 3)

    result = {
        "merchant": merchant,
        "category": category,
        "risk_score": risk_score,
        "risk_label": (
            "critical" if risk_score > 0.75 else
            "high" if risk_score > 0.5 else
            "medium" if risk_score > 0.25 else
            "low"
        ),
    }
    _merchant_risk_cache[cache_key] = result
    return result


# ─────────────────────────────────────────────
# TOOL 4: flag_geo_anomaly
# Detects if a transaction country is unexpected for an account
# ─────────────────────────────────────────────

def flag_geo_anomaly(tx_country: str, account_id: str) -> dict:
    """
    Compares transaction country against account's known home countries.
    Returns anomaly flag and detail.
    """
    rng = _seed_from_string(account_id)

    # Simulate account home country (in real system, fetched from AccountNode)
    home_countries = ["IN"]
    frequent_countries = rng.sample(["IN", "US", "SG", "AE", "GB"], k=rng.randint(1, 3))
    known_countries = set(home_countries + frequent_countries)

    is_anomaly = tx_country not in known_countries

    return {
        "is_anomaly": is_anomaly,
        "detail": (
            f"Transaction in {tx_country} — not in account's known countries {list(known_countries)}"
        ) if is_anomaly else f"Transaction country {tx_country} matches account profile",
        "tx_country": tx_country,
        "known_countries": list(known_countries),
    }
