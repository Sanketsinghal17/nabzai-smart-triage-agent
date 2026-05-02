from fastapi import FastAPI
from pydantic import BaseModel
from decision_engine import analyze_case
from scheduler import get_doctor_and_slot
from planner import get_steps
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PatientInput(BaseModel):
    symptoms: list
    severity: str
    duration_days: int

@app.post("/analyze")
def analyze(data: PatientInput):
    decision = analyze_case(
    symptoms=data.symptoms,
    severity=data.severity,
    duration_days=data.duration_days
    )

    doctor_data = get_doctor_and_slot(
        decision["specialist"]
    )

    return {
        **decision,
        **doctor_data,
        "steps": get_steps()
    }