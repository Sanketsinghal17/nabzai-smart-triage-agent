import json
import os

def get_doctor_and_slot(specialist):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "data", "doctors.json")

    with open(file_path, "r") as f:
        doctors = json.load(f)

    for doctor in doctors:
        if doctor["specialty"].lower() == specialist.lower():
            return {
                "doctor": doctor["name"],
                "slot": doctor["available_slots"][0],
                "location": doctor["location"]
            }

    return {
        "doctor": "No doctor available",
        "slot": "N/A",
        "location": "N/A"
    }