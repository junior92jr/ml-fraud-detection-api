from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums import MerchantCategory


class TransactionBase(BaseModel):
    """Base model for transaction schemas, common fields and validation"""

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
    """Represents a transaction read from the db, includes the auto-generated"""

    id: int

    model_config = ConfigDict(from_attributes=True)


class ScoreRequest(TransactionBase):
    """Fraud scoring request payload"""

    pass


class TransactionUpdate(BaseModel):
    """Used for updating transaction details, all fields are optional"""

    amount: float | None = Field(default=None, gt=0)
    transaction_hour: int | None = Field(default=None, ge=0, le=23)
    merchant_category: MerchantCategory | None = None
    foreign_transaction: bool | None = None
    location_mismatch: bool | None = None
    device_trust_score: int | None = Field(default=None, ge=0, le=100)
    velocity_last_24h: int | None = Field(default=None, ge=0)
    cardholder_age: int | None = Field(default=None, ge=18, le=100)


class ScoreResponse(BaseModel):
    """Response model for fraud scoring results"""

    transaction_id: str
    fraud_probability: float = Field(ge=0, le=1)
    decision: int
    threshold: float
    scored_at: datetime


class PredictionRead(BaseModel):
    """Represents a prediction read from the db, includes the auto-generated fields"""

    id: int
    transaction_id: str
    fraud_probability: float = Field(ge=0, le=1)
    decision: int
    scored_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionDetailResponse(BaseModel):
    """Detailed response model for a transaction,
    includes transaction details and all associated predictions"""

    transaction: TransactionRead
    predictions: list[PredictionRead]


class TransactionsCountResponse(BaseModel):
    """Total number of transactions for pagination controls"""

    total: int


class TransactionImportError(BaseModel):
    """Represents an error that occurred during transaction import"""

    line: int
    transaction_id: str | None = None
    error: str


class TransactionImportResponse(BaseModel):
    """Response model for transaction import results"""

    total_rows: int
    imported: int
    skipped_duplicates: int
    skipped_invalid: int
    skipped_scoring_errors: int
    errors: list[TransactionImportError]
