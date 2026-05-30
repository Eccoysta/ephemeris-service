from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from calculator import calculate_birth_chart
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Ephemeris Service", version="1.0.0")


class ChartRequest(BaseModel):
    birth_date: str       # "1995-06-15"
    birth_time: str       # "14:30"
    birth_lat: float      # 41.0082
    birth_lng: float      # 28.9784
    timezone: str         # "Europe/Istanbul"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/calculate")
def calculate(req: ChartRequest):
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
        logging.error(f"Chart calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
