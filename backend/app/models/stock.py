from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime

from app.db.database import Base


class StockTicker(Base):
    __tablename__ = "stock_tickers"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)
    company_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)