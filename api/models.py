from tortoise import fields
from tortoise.models import Model

from api.enums import MerchantCategory


class Transaction(Model):
    """Represents a financial transaction with various attributes used for fraud detection"""

    transaction_id = fields.CharField(max_length=255, unique=True)
    amount = fields.FloatField()
    transaction_hour = fields.IntField()
    merchant_category = fields.CharEnumField(MerchantCategory, max_length=100)
    foreign_transaction = fields.BooleanField()
    location_mismatch = fields.BooleanField()
    device_trust_score = fields.IntField()
    velocity_last_24h = fields.IntField()
    cardholder_age = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)


class Prediction(Model):
    """Represents a prediction for a financial transaction"""

    transaction: fields.ForeignKeyRelation[Transaction] = fields.ForeignKeyField(
        "models.Transaction",
        related_name="predictions",
    )
    fraud_probability = fields.FloatField()
    decision = fields.IntField()
    scored_at = fields.DatetimeField(auto_now_add=True)
