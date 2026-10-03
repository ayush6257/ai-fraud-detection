from pydantic import BaseModel, Field


class TransactionInput(BaseModel):
    account_id: str = Field(..., min_length=1)
    timestamp: str = Field(default="2024-08-17 03:20:00")
    amount: float = Field(..., gt=0)
    merchant: str = Field(..., min_length=1)
    merchant_city: str = Field(..., min_length=1)
    merchant_country: str = Field(default="US", min_length=1)
    channel: str = Field(default="online")
    currency: str = Field(default="USD", min_length=1)
