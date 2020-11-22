import uvicorn
from fastapi import FastAPI
from typing import Optional

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int) -> dict:
    return {"item_id": item_id}


if __name__ == "__main__":
    # uvicorn.run(app, host="127.0.0.1", port=8000)  # without reload

    uvicorn.run("main1:app", host="127.0.0.1", port=8000, reload=True)

