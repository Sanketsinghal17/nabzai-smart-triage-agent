from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# scheduler (your work)
from scheduler import (
    schedule_appointment,
    get_available_doctor,
    load_doctors,
)

# integration (main branch)
from decision_engine import analyze_case
from planner import get_steps


# ------------------------------------------------------------------
# App setup
# ------------------------------------------------------------------

app = FastAPI(
    title="NabzAI API",
    description="AI-powered healthcare triage + scheduling",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# Request model
# ------------------------------------------------------------------

class PatientInput(BaseModel):
    symptoms: list
    severity: str
    duration_days: int


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------

@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "NabzAI API running"
    }


# ------------------------------------------------------------------
# Full AI endpoint
# ------------------------------------------------------------------

@app.post("/analyze")
def analyze(data: PatientInput):

    # decision engine
    decision = analyze_case(
        symptoms=data.symptoms,
        severity=data.severity,
        duration_days=data.duration_days
    )

    # scheduler (your module)
    doctor_data = get_available_doctor(
        decision["specialist"]
    )

    return {
        **decision,
        **doctor_data,
        "steps": get_steps()
    }


# ------------------------------------------------------------------
# Debug scheduler endpoint
# ------------------------------------------------------------------

@app.get("/api/schedule")
def api_schedule(
    specialist: str = Query(...),
    location: str = Query(None),
):

    result = get_available_doctor(
        specialist,
        location=location
    )

    if result.get("doctor") is None:
        raise HTTPException(
            status_code=404,
            detail="No doctor found"
        )

    return result


# ------------------------------------------------------------------
# Reload doctor dataset
# ------------------------------------------------------------------

@app.get("/api/doctors/reload")
def reload_doctors():

    data = load_doctors(force_reload=True)

    return {
        "status": "reloaded",
        "doctor_count": len(data)
    }
