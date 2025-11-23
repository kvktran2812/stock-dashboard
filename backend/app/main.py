# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import Base, engine
from app.routers import tickers

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="API for managing stock tickers to monitor",
    version=settings.VERSION,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For localhost development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tickers.router)


@app.get("/")
def read_root():
    return {
        "message": "Stock Monitor API",
        "version": settings.VERSION,
        "endpoints": {
            "add_ticker": "POST /tickers",
            "list_tickers": "GET /tickers",
            "get_ticker": "GET /tickers/{ticker}",
            "update_ticker": "PATCH /tickers/{ticker}",
            "delete_ticker": "DELETE /tickers/{ticker}",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
