"""
seed_data.py — FraudGraph
Generates realistic accounts, transactions (clean + fraudulent), and merchant data.
Adapted from FinFlow360's seed_data.py pattern.
"""

from database import SessionLocal, init_db, Account, Transaction, FraudCase, MerchantRisk
from faker import Faker
import random
import uuid
import json
from datetime import datetime, timedelta

fake = Faker("en_IN")
random.seed(42)


MERCHANTS = [
    ("QuickMart", "grocery", "IN", 0.05),
    ("PayEase", "utilities", "IN", 0.05),
    ("TravelPro", "travel", "IN", 0.30),
    ("GlobalElec", "electronics", "IN", 0.50),
    ("CryptoXchange", "crypto", "SG", 0.85),
    ("LuxJewels", "jewelry", "AE", 0.65),
    ("BetWin", "gambling", "MT", 0.80),
    ("FastFoods", "food", "IN", 0.08),
    ("WireGlobal", "wire_transfer", "US", 0.75),
    ("ShopZone", "retail", "IN", 0.12),
    ("FuelStop", "fuel", "IN", 0.06),
    ("PharmaCare", "pharmacy", "IN", 0.04),
]

COUNTRIES = ["IN", "IN", "IN", "IN", "US", "GB", "SG", "AE", "NG", "RU", "CN", "MT"]


def make_tx_id():
    return "TX-" + str(uuid.uuid4())[:12].upper()


def make_account_id():
    return "ACC-" + str(uuid.uuid4())[:8].upper()


def seed():
    init_db()
    db = SessionLocal()

    # Clear existing data
    db.query(Transaction).delete()
    db.query(Account).delete()
    db.query(FraudCase).delete()
    db.query(MerchantRisk).delete()
    db.commit()

    # ── Seed Merchant Risk Table ──────────────────────────────────────────────
    for name, cat, country, fraud_rate in MERCHANTS:
        db.add(MerchantRisk(
            merchant_name=name,
            category=cat,
            country=country,
            fraud_rate=fraud_rate,
            transaction_volume=random.randint(500, 50000),
            risk_score=fraud_rate,
        ))

    # ── Seed Accounts ─────────────────────────────────────────────────────────
    accounts = []
    tiers = ["low"] * 8 + ["medium"] * 4 + ["high"] * 3 + ["critical"] * 2

    for i in range(17):
        acc_id = make_account_id()
        tier = tiers[i]
        fraud_score = {
            "low": random.uniform(5, 25),
            "medium": random.uniform(26, 50),
            "high": random.uniform(51, 75),
            "critical": random.uniform(76, 95),
        }[tier]

        account = Account(
            account_id=acc_id,
            user_name=fake.name(),
            email=fake.email(),
            account_age_days=random.randint(30, 2000),
            avg_monthly_spend=round(random.uniform(10000, 500000), 2),
            home_country="IN",
            risk_tier=tier,
            fraud_score=round(fraud_score, 2),
            flagged=tier in ["high", "critical"],
        )
        db.add(account)
        accounts.append((acc_id, tier, fraud_score))

    # ── Seed Transactions ─────────────────────────────────────────────────────
    for acc_id, tier, fraud_score in accounts:
        tx_count = random.randint(5, 25)
        base_date = datetime.utcnow() - timedelta(days=30)

        for j in range(tx_count):
            tx_ts = base_date + timedelta(
                days=random.randint(0, 29),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            # Higher-risk tiers get more suspicious transactions
            is_suspicious = random.random() < (fraud_score / 100)

            if is_suspicious:
                merchant_name, cat, country, _ = random.choice(
                    [m for m in MERCHANTS if m[3] > 0.4]
                )
                amount = round(random.uniform(50000, 500000), 2)
                # Suspicious: round number
                if random.random() > 0.5:
                    amount = round(amount / 10000) * 10000
                country = random.choice(["NG", "RU", "MT", "CN"]) if random.random() > 0.5 else country
                # Odd hours
                tx_ts = tx_ts.replace(hour=random.randint(0, 4))
                fraud_prob = round(random.uniform(0.6, 0.99), 3)
                reasons = random.sample(
                    ["unusual_amount", "geo_anomaly", "velocity_spike",
                     "high_risk_merchant", "unusual_hour_transaction", "device_mismatch"],
                    k=random.randint(1, 4),
                )
                status = "flagged"
            else:
                merchant_name, cat, country_m, _ = random.choice(
                    [m for m in MERCHANTS if m[3] < 0.3]
                )
                country = "IN"
                amount = round(random.uniform(500, 30000), 2)
                fraud_prob = round(random.uniform(0.0, 0.3), 3)
                reasons = []
                status = "normal"

            db.add(Transaction(
                tx_id=make_tx_id(),
                account_id=acc_id,
                amount=amount,
                merchant=merchant_name,
                merchant_category=cat,
                country=country,
                timestamp=tx_ts,
                device_fingerprint="DEV-" + str(uuid.uuid4())[:8].upper(),
                ip_address=fake.ipv4(),
                is_flagged=is_suspicious,
                fraud_probability=fraud_prob,
                anomaly_reasons=json.dumps(reasons),
                status=status,
            ))

    # ── Seed Fraud Cases for high/critical accounts ───────────────────────────
    for acc_id, tier, _ in accounts:
        if tier in ["high", "critical"]:
            db.add(FraudCase(
                case_id="CASE-" + acc_id,
                account_id=acc_id,
                tx_ids=json.dumps([make_tx_id() for _ in range(random.randint(1, 4))]),
                severity=tier,
                reason_summary="Multiple anomaly patterns detected: geo mismatch + velocity spike",
                recommended_action="freeze_card" if tier == "critical" else "flag_for_review",
                status="open",
                assigned_to="human_review" if tier == "critical" else "auto",
            ))

    db.commit()
    db.close()
    print("✅ FraudGraph database seeded successfully!")
    print(f"   → 17 accounts | {sum(1 for _, t, _ in accounts if t in ['high','critical'])} flagged")
    print(f"   → {len(MERCHANTS)} merchants | transactions seeded")


if __name__ == "__main__":
    seed()
