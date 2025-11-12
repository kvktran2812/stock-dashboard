from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import yfinance as yf

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./stock_monitor.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class StockTicker(Base):
    __tablename__ = "stock_tickers"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)
    company_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for API
class TickerCreate(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL"
            }
        }

class TickerResponse(BaseModel):
    id: int
    ticker: str
    company_name: Optional[str]
    is_active: bool
    added_at: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True

class TickerUpdate(BaseModel):
    is_active: Optional[bool] = None

# FastAPI app
app = FastAPI(
    title="Stock Monitor API",
    description="API for managing stock tickers to monitor",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For localhost development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to validate and get stock info
def get_stock_info(ticker: str) -> Optional[str]:
    """Validate ticker and return company name"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        # Check if ticker is valid
        if 'symbol' in info or 'shortName' in info:
            return info.get('shortName', info.get('longName', ticker))
        return None
    except Exception:
        return None

# API Routes
@app.get("/")
def read_root():
    return {
        "message": "Stock Monitor API",
        "version": "1.0.0",
        "endpoints": {
            "add_ticker": "POST /tickers",
            "list_tickers": "GET /tickers",
            "get_ticker": "GET /tickers/{ticker}",
            "update_ticker": "PATCH /tickers/{ticker}",
            "delete_ticker": "DELETE /tickers/{ticker}"
        }
    }

@app.post("/tickers", response_model=TickerResponse, status_code=201)
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
    
    # Create new ticker
    new_ticker = StockTicker(
        ticker=ticker,
        company_name=company_name
    )
    
    db.add(new_ticker)
    db.commit()
    db.refresh(new_ticker)
    
    return new_ticker

@app.get("/tickers", response_model=List[TickerResponse])
def list_tickers(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """List all monitored tickers"""
    query = db.query(StockTicker)
    
    if active_only:
        query = query.filter(StockTicker.is_active == True)
    
    tickers = query.order_by(StockTicker.ticker).all()
    return tickers

@app.get("/tickers/{ticker}", response_model=TickerResponse)
def get_ticker(ticker: str, db: Session = Depends(get_db)):
    """Get details of a specific ticker"""
    ticker = ticker.upper().strip()
    stock = db.query(StockTicker).filter(StockTicker.ticker == ticker).first()
    
    if not stock:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")
    
    return stock

@app.patch("/tickers/{ticker}", response_model=TickerResponse)
def update_ticker(
    ticker: str,
    update_data: TickerUpdate,
    db: Session = Depends(get_db)
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

@app.delete("/tickers/{ticker}", status_code=204)
def delete_ticker(ticker: str, db: Session = Depends(get_db)):
    """Delete a ticker from monitoring"""
    ticker = ticker.upper().strip()
    stock = db.query(StockTicker).filter(StockTicker.ticker == ticker).first()
    
    if not stock:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")
    
    db.delete(stock)
    db.commit()
    
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)