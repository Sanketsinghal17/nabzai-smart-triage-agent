# NabzAI - Smart Healthcare Triage Agent

## Problem
Patients often waste time figuring out:
- Which doctor to consult
- How urgent their condition is
- How to quickly book appointments

This causes delays in healthcare access.

---

## Solution
NabzAI is an Agentic AI healthcare assistant that:

- Analyzes patient symptoms
- Detects urgency level
- Recommends correct specialist
- Assigns available doctor
- Books appointment slot
- Generates printable appointment slip

---

## Features
✅ Symptom selection  
✅ Custom symptom input  
✅ Patient name & age collection  
✅ AI triage engine  
✅ Specialist recommendation  
✅ Doctor scheduling  
✅ Appointment booking  
✅ Printable appointment slip  

---

## Tech Stack
Frontend:
- React
- Vite
- CSS

Backend:
- FastAPI
- Python

AI Logic:
- Rule-based Agentic Decision Engine

Database:
- JSON doctor dataset

---

## Project Flow

Patient Details → Symptom Analysis → Urgency Detection → Specialist Mapping → Doctor Assignment → Appointment Booking → Print Slip

---

## How to Run

### Frontend
```bash
cd frontend
npm install
npm run dev

### Backend
```bash
cd backend
uvicorn main:app --reload