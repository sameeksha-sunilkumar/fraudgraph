"""routers/dashboard.py — FraudGraph"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, Account, Transaction, FraudCase, AgentScanLog

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_accounts = db.query(Account).count()
    flagged_accounts = db.query(Account).filter(Account.flagged == True).count()
    total_tx = db.query(Transaction).count()
    flagged_tx = db.query(Transaction).filter(Transaction.is_flagged == True).count()
    open_cases = db.query(FraudCase).filter(FraudCase.status == "open").count()
    critical_cases = db.query(FraudCase).filter(
        FraudCase.severity == "critical", FraudCase.status == "open"
    ).count()

    # Risk tier distribution
    tiers = {}
    for tier in ["low", "medium", "high", "critical"]:
        tiers[tier] = db.query(Account).filter(Account.risk_tier == tier).count()

    # Recent agent activity
    recent_scans = db.query(AgentScanLog).order_by(
        AgentScanLog.created_at.desc()
    ).limit(5).all()

    return {
        "accounts": {
            "total": total_accounts,
            "flagged": flagged_accounts,
            "clean": total_accounts - flagged_accounts,
        },
        "transactions": {
            "total": total_tx,
            "flagged": flagged_tx,
            "flag_rate": round(flagged_tx / max(total_tx, 1) * 100, 1),
        },
        "cases": {
            "open": open_cases,
            "critical": critical_cases,
        },
        "risk_distribution": tiers,
        "recent_agent_activity": [
            {
                "scan_id": s.scan_id,
                "walker": s.walker_name,
                "account_id": s.account_id,
                "duration_ms": s.duration_ms,
                "timestamp": str(s.created_at),
            }
            for s in recent_scans
        ],
    }


@router.get("/risk-chart")
def get_risk_chart(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return [
        {
            "account_id": a.account_id,
            "user_name": a.user_name,
            "fraud_score": a.fraud_score,
            "risk_tier": a.risk_tier,
            "flagged": a.flagged,
        }
        for a in accounts
    ]
