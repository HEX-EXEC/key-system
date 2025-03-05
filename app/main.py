# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routes import keys, blacklist
from app.auth import router as auth_router
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Include routers
app.include_router(auth_router)
app.include_router(keys.router, prefix="/keys", tags=["keys"])
app.include_router(blacklist.router, prefix="/blacklist", tags=["blacklist"])
app.mount("/static", StaticFiles(directory="static"), name="static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application lifespan")
    try:
        with engine.begin() as conn:
            logger.info("Creating database tables")
            Base.metadata.create_all(bind=conn)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error during database setup: {str(e)}")
        raise
    try:
        logger.info("Application startup complete")
        yield
    finally:
        logger.info("Disposing engine")
        engine.dispose()
        logger.info("Application shutdown complete")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root(request: Request):
    logger.info(f"Received request: {request.method} {request.url}")
    try:
        with open("index.html", "r") as f:
            content = f.read()
        logger.info("Successfully read index.html")
        return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
        raise