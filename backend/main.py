from fastapi import FastAPI
from scheduler import schedule_appointment

app = FastAPI()

@app.get("/")
def home():
    return {"message": "NabzAI running"}

@app.get("/schedule")
def get_schedule(specialist: str, location: str = None):
    result = schedule_appointment(specialist, location)
    return result