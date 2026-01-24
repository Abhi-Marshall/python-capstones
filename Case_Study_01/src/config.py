"""
Configuration file for Hospital Appointment Management System
"""

import os
from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
REPORTS_DIR = PROJECT_ROOT / "reports"

PATIENT_DATA_FILE = DATA_DIR / "patient.json"
DOCTOR_DATA_FILE = DATA_DIR / "doctor.json"
APPOINTMENT_DATA_FILE = DATA_DIR / "appointment.json"

LOG_FILE = LOGS_DIR / "system.log"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# System Constants
SLOT_DURATION = 30  # minutes
DOCTOR_START_TIME = 10  # 10 AM
DOCTOR_END_TIME = 18  # 6 PM
TOTAL_SLOTS_PER_DAY = ((DOCTOR_END_TIME - DOCTOR_START_TIME) * 60) // SLOT_DURATION

# Medical Departments
DEPARTMENTS = {
    "1": "Cardiology",
    "2": "Neurology",
    "3": "Orthopedics",
    "4": "Dermatology",
    "5": "General Medicine",
    "6": "Pediatrics",
    "7": "Psychiatry",
    "8": "Urology"
}

# Logging Configuration
LOG_FORMAT = "[%(asctime)s] - [%(levelname)s] - [%(threadName)s] - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
