"""
main.py  -  NabzAI FastAPI Entry Point
=======================================
Routes
------
GET /                          Health check
GET /schedule                  (legacy) specialist + optional location
GET /api/schedule              Full response with score, experience, reason
GET /api/doctors/reload        Force-reload the doctor cache (dev/admin)
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scheduler import schedule_appointment, get_available_doctor, load_doctors

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="NabzAI Scheduling API",
    description="AI-powered healthcare triage — doctor scheduling module",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def home():
    """Health check."""
    return {"status": "ok", "message": "NabzAI Scheduling API is running"}


@app.get("/schedule", tags=["Legacy"])
def get_schedule(
    specialist: str = Query(..., description="Medical specialist type"),
    location: str = Query(None, description="Preferred city / area"),
):
    """
    Legacy endpoint — kept for backward compatibility.
    Returns doctor name and slot only.
    """
    result = schedule_appointment(specialist, location)
    if result.get("doctor") is None:
        raise HTTPException(status_code=404, detail=result.get("error", "No doctor found"))
    return result


@app.get("/api/schedule", tags=["Scheduling"])
def api_schedule(
    specialist: str = Query(..., description="Medical specialist type, e.g. 'Cardiologist'"),
    location: str  = Query(None, description="Preferred city, e.g. 'Delhi'"),
    randomize: bool = Query(False, description="Randomize doctor/slot selection"),
    top_n: int      = Query(3, ge=1, le=10, description="Pool size for randomised selection"),
):
    """
    Full scheduling endpoint.
    Returns doctor, slot, hospital, location, specialist, rating,
    experience, selection_score, and selection reason.
    """
    result = get_available_doctor(
        specialist,
        location=location,
        top_n=top_n,
        randomize=randomize,
    )
    if result.get("doctor") is None:
        raise HTTPException(status_code=404, detail=result.get("error", "No doctor found"))
    return result


@app.get("/api/doctors/reload", tags=["Admin"])
def reload_doctors():
    """Force-reload the doctor cache from disk (useful after updating doctors.json)."""
    data = load_doctors(force_reload=True)
    return {"status": "reloaded", "doctor_count": len(data)}