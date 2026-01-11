from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, unique=True, nullable=False)

    amount = Column(Float, nullable=False)
    transaction_hour = Column(Integer, nullable=False)
    merchant_category = Column(String, nullable=False)
    foreign_transaction = Column(Boolean, nullable=False)
    location_mismatch = Column(Boolean, nullable=False)
    device_trust_score = Column(Integer, nullable=False)
    velocity_last_24h = Column(Integer, nullable=False)
    cardholder_age = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(
        String, ForeignKey("transactions.transaction_id"), nullable=False
    )
    fraud_probability = Column(Float, nullable=False)
    decision = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    scored_at = Column(DateTime, default=datetime.now(timezone.utc))
