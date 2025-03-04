# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routes import keys, blacklist
from contextlib import contextmanager

app = FastAPI()

app.include_router(keys.router, prefix="/keys", tags=["keys"])
app.include_router(blacklist.router, prefix="/blacklist", tags=["blacklist"])
app.mount("/static", StaticFiles(directory="static"), name="static")

@contextmanager
def lifespan(app: FastAPI):
    # Create tables if they don't exist
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)
    yield
    # Optional cleanup (e.g., close engine connections if needed)
    engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    with open("index.html", "r") as f:
        return f.read()