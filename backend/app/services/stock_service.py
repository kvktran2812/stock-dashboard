# app/services/stock_service.py
from typing import Optional
import yfinance as yf


def get_stock_info(ticker: str) -> Optional[str]:
    """Validate ticker and return company name using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Check if ticker is valid
        if "symbol" in info or "shortName" in info:
            return info.get("shortName", info.get("longName", ticker))
        return None
    except Exception:
        return None
