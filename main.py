import uvicorn
import yfinance
from fastapi import BackgroundTasks, Depends, FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine
from models import Stock


class StockRequest(BaseModel):
    symbol: str


def get_db():
    """
    get connection to database
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


app = FastAPI()
templates = Jinja2Templates(directory="templates")
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def home(request: Request):
    """
    Home page
    """
    return templates.TemplateResponse("home.html", {"request": request})


def fetch_stock_data(id: int):

    db = SessionLocal()
    stock = db.query(Stock).filter(Stock.id == id).first()
    yahoo_data = yfinance.Ticker(stock.symbol)

    stock.ma200 = yahoo_data.info["twoHundredDayAverage"]
    stock.ma50 = yahoo_data.info["fiftyDayAverage"]
    stock.price = yahoo_data.info["previousClose"]
    stock.forward_pe = yahoo_data.info["forwardPE"]
    stock.forward_eps = yahoo_data.info["forwardEps"]

    if yahoo_data.info["dividendYield"] is not None:
        stock.dividend_yield = yahoo_data.info["dividendYield"] * 100

    db.add(stock)
    db.commit()


@app.post("/stock")
async def create_stock(
    stock_request: StockRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    fetch stock data and store in database
    """
    stock = Stock()
    stock.symbol = stock_request.symbol

    db.add(stock)
    db.commit()

    background_tasks.add_task(fetch_stock_data, stock.id)

    return {"code": "success", "message": "stock was added to the database"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
