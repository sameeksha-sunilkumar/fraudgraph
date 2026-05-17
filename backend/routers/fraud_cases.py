"""routers/fraud_cases.py — FraudGraph"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, FraudCase
import json

router = APIRouter(prefix="/cases", tags=["Fraud Cases"])


@router.get("/")
def list_cases(db: Session = Depends(get_db)):
    cases = db.query(FraudCase).order_by(FraudCase.created_at.desc()).all()
    return [_serialize(c) for c in cases]


@router.get("/open")
def get_open_cases(db: Session = Depends(get_db)):
    cases = db.query(FraudCase).filter(FraudCase.status == "open").all()
    return [_serialize(c) for c in cases]


@router.patch("/{case_id}/resolve")
def resolve_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(FraudCase).filter(FraudCase.case_id == case_id).first()
    if not case:
        return {"error": "Case not found"}
    case.status = "resolved"
    db.commit()
    return {"message": f"Case {case_id} resolved"}


@router.patch("/{case_id}/false-positive")
def mark_false_positive(case_id: str, db: Session = Depends(get_db)):
    case = db.query(FraudCase).filter(FraudCase.case_id == case_id).first()
    if not case:
        return {"error": "Case not found"}
    case.status = "false_positive"
    db.commit()
    return {"message": f"Case {case_id} marked as false positive"}


def _serialize(c: FraudCase) -> dict:
    return {
        "case_id": c.case_id,
        "account_id": c.account_id,
        "tx_ids": json.loads(c.tx_ids) if c.tx_ids else [],
        "severity": c.severity,
        "reason_summary": c.reason_summary,
        "recommended_action": c.recommended_action,
        "status": c.status,
        "assigned_to": c.assigned_to,
        "created_at": str(c.created_at),
    }
