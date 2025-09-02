import json
import os
from langchain_core.tools import tool


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
    return f"Appointment saved for {patient} with {doctor} on {date} {time}"


@tool
def get_docs(user_message: str):
    """
    Get doctor information from the Qdrant vector database.

    Use ONLY when the user provides a clear symptom or condition
    (e.g., "chest pain", "skin rash").
    Do NOT call this tool for vague inputs like "I am sick" —
    instead, ask follow-up questions first.
    """

    from main import app

    results = app.state.appointment_agent.qdrant.search(user_message)
    content = "\n".join([doc.page_content for doc in results])
    return content
