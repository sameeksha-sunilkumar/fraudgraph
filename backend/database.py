"""
database.py — FraudGraph
SQLAlchemy models adapted from FinFlow360 for fraud detection domain.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./fraudgraph.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)


# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, unique=True, index=True)
    user_name = Column(String)
    email = Column(String)
    account_age_days = Column(Integer, default=365)
    avg_monthly_spend = Column(Float, default=50000.0)
    home_country = Column(String, default="IN")
    risk_tier = Column(String, default="low")    # low | medium | high | critical
    fraud_score = Column(Float, default=0.0)
    flagged = Column(Boolean, default=False)
    last_scan = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    tx_id = Column(String, unique=True, index=True)
    account_id = Column(String, index=True)
    amount = Column(Float)
    merchant = Column(String)
    merchant_category = Column(String)
    country = Column(String, default="IN")
    timestamp = Column(DateTime, default=datetime.utcnow)
    device_fingerprint = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    is_flagged = Column(Boolean, default=False)
    fraud_probability = Column(Float, default=0.0)
    anomaly_reasons = Column(Text, default="[]")   # JSON list stored as text
    status = Column(String, default="normal")      # normal | flagged | confirmed_fraud | false_positive


class FraudCase(Base):
    __tablename__ = "fraud_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, unique=True, index=True)
    account_id = Column(String, index=True)
    tx_ids = Column(Text, default="[]")            # JSON list
    severity = Column(String)                      # low | medium | high | critical
    reason_summary = Column(Text)
    recommended_action = Column(String)
    status = Column(String, default="open")        # open | under_review | resolved | false_positive
    assigned_to = Column(String, default="auto")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


class AgentScanLog(Base):
    """Tracks every Jac walker execution for audit trail."""
    __tablename__ = "agent_scan_logs"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String, unique=True, index=True)
    walker_name = Column(String)
    account_id = Column(String, nullable=True)
    result_summary = Column(Text)
    duration_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class MerchantRisk(Base):
    __tablename__ = "merchant_risks"

    id = Column(Integer, primary_key=True, index=True)
    merchant_name = Column(String, unique=True, index=True)
    category = Column(String)
    country = Column(String, default="IN")
    fraud_rate = Column(Float, default=0.0)
    transaction_volume = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
