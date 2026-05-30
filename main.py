from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import sys
import os

# Add current dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ephemeris Service", version="1.0.0")

# Try importing calculator
try:
    from calculator import calculate_birth_chart
    logger.info("Calculator imported successfully")
except Exception as e:
    logger.error(f"Failed to import calculator: {e}")
    calculate_birth_chart = None


class ChartRequest(BaseModel):
    birth_date: str
    birth_time: str
    birth_lat: float
    birth_lng: float
    timezone: str


@app.get("/")
def root():
    return {
        "service": "ephemeris-service",
        "status": "ok",
        "version": "1.0.0",
        "endpoints": ["/health", "/calculate", "/test"]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test")
def test():
    return {
        "calculator_loaded": calculate_birth_chart is not None,
        "python_version": sys.version,
    }


@app.post("/calculate")
def calculate(req: ChartRequest):
    if calculate_birth_chart is None:
        raise HTTPException(status_code=500, detail="Calculator not loaded")

    try:
        chart = calculate_birth_chart(
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            birth_lat=req.birth_lat,
            birth_lng=req.birth_lng,
            timezone=req.timezone,
        )
        return chart
    except Exception as e:
        logger.error(f"Chart calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
