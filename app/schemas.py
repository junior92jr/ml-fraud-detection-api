from typing import Literal

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int

    class Config:
        from_attributes = True


MerchantCategory = Literal[
    "Electronics",
    "Travel",
    "Grocery",
    "Food",
    "Clothing",
]


class TransactionBase(BaseModel):
    transaction_id: str
    amount: float = Field(gt=0)
    transaction_hour: int = Field(ge=0, le=23)
    merchant_category: MerchantCategory
    foreign_transaction: bool
    location_mismatch: bool
    device_trust_score: int = Field(ge=0, le=100)
    velocity_last_24h: int = Field(ge=0)
    cardholder_age: int = Field(ge=18, le=100)


class TransactionCreate(TransactionBase):
    """Used internally for CSV import or API ingestion"""

    pass


class TransactionRead(TransactionBase):
    id: int

    class Config:
        from_attributes = True


class ScoreRequest(TransactionBase):
    """Fraud scoring request payload"""

    pass


class ScoreResponse(BaseModel):
    transaction_id: str
    fraud_probability: float = Field(ge=0, le=1)
    decision: Literal["approve", "review", "reject"]
    threshold: float
    model_version: str
    scored_at: str

    orm_mode = True


class FraudPredictionRequest(BaseModel):
    transaction_id: int | None = None

    amount: float = Field(ge=0)
    transaction_hour: int = Field(ge=0, le=23)
    merchant_category: str
    foreign_transaction: int = Field(ge=0, le=1)
    location_mismatch: int = Field(ge=0, le=1)
    device_trust_score: float
    velocity_last_24h: int = Field(ge=0)
    cardholder_age: int = Field(ge=0)


class FraudPredictionResponse(BaseModel):
    transaction_id: int | None
    is_fraud_pred: int
    fraud_probability: float
