from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.routing import APIRoute, Mount
from app.database import engine, Base  # Absolute import
from app.auth import router as auth_router  # Absolute import
from app.routes.keys import router as keys_router  # Absolute import
from app.routes.blacklist import router as blacklist_router  # Absolute import
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

app = FastAPI(lifespan=lifespan, redirect_slashes=False)

# Include routers with logging
logger.info("Including auth_router")
app.include_router(auth_router)
logger.info("Including keys_router")
app.include_router(keys_router, prefix="/api/keys")
logger.info("Including blacklist_router")
app.include_router(blacklist_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Log all registered routes
logger.info("Registered routes:")
for route in app.routes:
    if isinstance(route, APIRoute):
        logger.info(f"Route: {route.path}, Methods: {route.methods}")
    elif isinstance(route, Mount):
        logger.info(f"Mount: {route.path}")
    else:
        logger.info(f"Other route: {route.path}")

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

@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint works"}