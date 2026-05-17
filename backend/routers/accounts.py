"""routers/accounts.py — FraudGraph"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, Account

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("/")
def list_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return [
        {
            "account_id": a.account_id,
            "user_name": a.user_name,
            "email": a.email,
            "account_age_days": a.account_age_days,
            "avg_monthly_spend": a.avg_monthly_spend,
            "home_country": a.home_country,
            "risk_tier": a.risk_tier,
            "fraud_score": a.fraud_score,
            "flagged": a.flagged,
            "last_scan": str(a.last_scan) if a.last_scan else None,
        }
        for a in accounts
    ]


@router.get("/{account_id}")
def get_account(account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account:
        return {"error": "Account not found"}
    return {
        "account_id": account.account_id,
        "user_name": account.user_name,
        "email": account.email,
        "account_age_days": account.account_age_days,
        "avg_monthly_spend": account.avg_monthly_spend,
        "home_country": account.home_country,
        "risk_tier": account.risk_tier,
        "fraud_score": account.fraud_score,
        "flagged": account.flagged,
    }


@router.get("/flagged/list")
def get_flagged_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.flagged == True).all()
    return [
        {
            "account_id": a.account_id,
            "user_name": a.user_name,
            "risk_tier": a.risk_tier,
            "fraud_score": a.fraud_score,
        }
        for a in accounts
    ]
