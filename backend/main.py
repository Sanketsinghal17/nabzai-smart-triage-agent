from fastapi import FastAPI
from pydantic import BaseModel
from decision_engine import analyze_case
from scheduler import get_doctor_and_slot
from planner import get_steps

app = FastAPI()

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