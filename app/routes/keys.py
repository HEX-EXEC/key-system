from fastapi import APIRouter, HTTPException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading keys.py module")

router = APIRouter()

logger.info("Defining create_key endpoint")
@router.post("/")
async def create_key():
    logger.info("create_key endpoint called")
    return {"message": "Key created successfully"}

if __name__ == "__main__":
    print("Successfully loaded keys.py")