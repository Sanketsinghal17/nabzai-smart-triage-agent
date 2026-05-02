# NabzAI - Smart Healthcare Triage Agent

## Problem Statement
Patients often waste time figuring out:
- Which doctor to consult
- Whether their condition is urgent
- How to quickly book appointments

This causes delays in healthcare systems.

---

# Solution
NabzAI is an AI-powered healthcare triage platform that:

- Analyzes patient symptoms
- Detects urgency level
- Recommends correct specialist
- Finds available doctors
- Books appointment slots
- Generates printable appointment slips

---

# How It Works

Patient Details → Symptom Input → AI Analysis → Specialist Recommendation → Doctor Scheduling → Appointment Booking → Print Slip

---

# Tech Stack

## Frontend
- React
- Vite
- CSS

## Backend
- FastAPI
- Python

## Deployment
- Vercel
- Render

## Database
- JSON doctor dataset

---

# Agent Workflow

1. Accept symptoms
2. Analyze severity
3. Detect urgency
4. Recommend specialist
5. Find available doctor
6. Assign slot
7. Generate confirmation slip

---

# Architecture Diagram

Frontend (React)

↓

Backend API (FastAPI)

↓

Decision Engine

↓

Scheduler Engine

↓

Doctor Database

↓

Appointment Confirmation

---

# API Documentation

## POST /analyze

Request:

```json
{
  "symptoms": ["chest pain", "breathing issue"],
  "severity": "Severe",
  "duration_days": "2"
}
```

Response:

```json
{
  "urgency": "High",
  "specialist": "Cardiologist",
  "secondary_specialist": "Pulmonologist",
  "doctor": "Dr Aisha Khan",
  "slot": "09:00"
}
```

---

# Test Cases

### Case 1
Chest pain + breathing issue

Expected:
Cardiologist

---

### Case 2
Headache + dizziness

Expected:
Neurologist

---

### Case 3
Skin rash

Expected:
Dermatologist

---

# Setup Instructions

## Frontend
```bash
cd frontend
npm install
npm run dev
```

## Backend
```bash
cd backend
uvicorn main:app --reload
```

---

# Live Deployment

Frontend:
https://nabzai-smart-triage-agent.vercel.app/

Backend:
https://nabzai-smart-triage-agent.onrender.com

---


# Team Contributions

Person 1 → Decision Engine

Person 2 → Frontend UI

Person 3 → Scheduler

Person 4 → Integration + Deployment