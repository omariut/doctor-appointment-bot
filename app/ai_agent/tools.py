import json
import os
from langchain_core.tools import tool
from datetime import datetime

APPOINTMENTS_FILE = "app/ai_agent/appointments.json"


@tool
def save_appointment(doctor: str, patient: str, date: str, time: str) -> str:
    """Save appointment details into a JSON file."""
    appointment = {"doctor": doctor, "patient": patient, "date": date, "time": time}

    # Ensure file exists and is a valid JSON array
    if not os.path.exists(APPOINTMENTS_FILE):
        with open(APPOINTMENTS_FILE, "w") as f:
            json.dump([], f)

    with open(APPOINTMENTS_FILE, "r+") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
        data.append(appointment)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    print(f" Appointment saved for {patient} with Dr. {doctor} on {date} {time}")
    return f"Appointment saved for {patient} with Dr. {doctor} on {date} {time}"
