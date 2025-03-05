# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routes import keys, blacklist
from contextlib import asynccontextmanager

app = FastAPI()

app.include_router(keys.router, prefix="/keys", tags=["keys"])
app.include_router(blacklist.router, prefix="/blacklist", tags=["blacklist"])
app.mount("/static", StaticFiles(directory="static"), name="static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)
    try:
        yield
    finally:
        engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)  # Remove methods=["GET", "HEAD"]
async def read_root(request: Request):
    with open("index.html", "r") as f:
        return f.read()