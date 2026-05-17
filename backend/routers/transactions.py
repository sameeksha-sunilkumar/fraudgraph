"""routers/transactions.py — FraudGraph"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, Transaction
import json

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/")
def list_transactions(limit: int = 50, db: Session = Depends(get_db)):
    txs = db.query(Transaction).order_by(Transaction.timestamp.desc()).limit(limit).all()
    return [_serialize(t) for t in txs]


@router.get("/flagged")
def get_flagged_transactions(db: Session = Depends(get_db)):
    txs = db.query(Transaction).filter(Transaction.is_flagged == True).order_by(
        Transaction.fraud_probability.desc()
    ).all()
    return [_serialize(t) for t in txs]


@router.get("/account/{account_id}")
def get_account_transactions(account_id: str, db: Session = Depends(get_db)):
    txs = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).order_by(Transaction.timestamp.desc()).all()
    return [_serialize(t) for t in txs]


def _serialize(t: Transaction) -> dict:
    return {
        "tx_id": t.tx_id,
        "account_id": t.account_id,
        "amount": t.amount,
        "merchant": t.merchant,
        "merchant_category": t.merchant_category,
        "country": t.country,
        "timestamp": str(t.timestamp),
        "is_flagged": t.is_flagged,
        "fraud_probability": t.fraud_probability,
        "anomaly_reasons": json.loads(t.anomaly_reasons) if t.anomaly_reasons else [],
        "status": t.status,
    }
