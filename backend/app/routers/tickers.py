# app/routers/tickers.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.stock import StockTicker
from app.schemas.stock import TickerCreate, TickerResponse, TickerUpdate
from app.services.stock_service import get_stock_info
from datetime import datetime

router = APIRouter(
    prefix="/tickers",
    tags=["tickers"],
)


@router.post("", response_model=TickerResponse, status_code=201)
def add_ticker(ticker_data: TickerCreate, db: Session = Depends(get_db)):
    """Add a new stock ticker to monitor"""
    ticker = ticker_data.ticker.upper().strip()

    # Check if ticker already exists
    existing = db.query(StockTicker).filter(StockTicker.ticker == ticker).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Ticker {ticker} already exists")

    # Validate ticker with yfinance
    company_name = get_stock_info(ticker)
    if company_name is None:
        raise HTTPException(status_code=404, detail=f"Invalid ticker symbol: {ticker}")

    new_ticker = StockTicker(
        ticker=ticker,
        company_name=company_name,
    )

    db.add(new_ticker)
    db.commit()
    db.refresh(new_ticker)

    return new_ticker


@router.get("", response_model=List[TickerResponse])
def list_tickers(
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """List all monitored tickers"""
    query = db.query(StockTicker)

    if active_only:
        query = query.filter(StockTicker.is_active == True)

    tickers = query.order_by(StockTicker.ticker).all()
    return tickers


@router.get("/{ticker}", response_model=TickerResponse)
def get_ticker(ticker: str, db: Session = Depends(get_db)):
    """Get details of a specific ticker"""
    ticker = ticker.upper().strip()
    stock = db.query(StockTicker).filter(StockTicker.ticker == ticker).first()

    if not stock:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")

    return stock


@router.patch("/{ticker}", response_model=TickerResponse)
def update_ticker(
    ticker: str,
    update_data: TickerUpdate,
    db: Session = Depends(get_db),
):
    """Update ticker (e.g., activate/deactivate monitoring)"""
    ticker = ticker.upper().strip()
    stock = db.query(StockTicker).filter(StockTicker.ticker == ticker).first()

    if not stock:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")

    if update_data.is_active is not None:
        stock.is_active = update_data.is_active

    stock.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(stock)

    return stock


@router.delete("/{ticker}", status_code=204)
def delete_ticker(ticker: str, db: Session = Depends(get_db)):
    """Delete a ticker from monitoring"""
    ticker = ticker.upper().strip()
    stock = db.query(StockTicker).filter(StockTicker.ticker == ticker).first()

    if not stock:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")

    db.delete(stock)
    db.commit()
    return None
