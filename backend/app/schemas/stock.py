# app/schemas/stock.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TickerCreate(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA)")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL"
            }
        }


class TickerUpdate(BaseModel):
    is_active: Optional[bool] = None


class TickerResponse(BaseModel):
    id: int
    ticker: str
    company_name: Optional[str]
    is_active: bool
    added_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True  # for ORM mode (SQLAlchemy models)