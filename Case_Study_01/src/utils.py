"""
Utility functions for Hospital Appointment Management System
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from config import LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT

# Setup Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create file handler
handler = logging.FileHandler(LOG_FILE)
handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)


def get_logger(name):
    """Get a logger with the specified name"""
    return logging.getLogger(name)


def load_json_file(file_path):
    """
    Load data from JSON file
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary if file exists, empty dict otherwise
    """
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            logger.info(f"Successfully loaded data from {file_path}")
            return data
    except json.JSONDecodeError:
        logger.warning(f"JSON decode error in {file_path}, returning empty dict")
        return {}
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        return {}


def save_json_file(file_path, data):
    """
    Save data to JSON file
    
    Args:
        file_path: Path to save JSON file
        data: Dictionary to save
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            logger.info(f"Successfully saved data to {file_path}")
    except Exception as e:
        logger.error(f"Error saving to {file_path}: {str(e)}")


def update_json_file(file_path, key, value):
    """
    Update a specific key in JSON file
    
    Args:
        file_path: Path to JSON file
        key: Key to update
        value: Value to set
    """
    data = load_json_file(file_path)
    data[key] = value
    save_json_file(file_path, data)


def get_next_id(file_path, prefix):
    """
    Generate next ID for patient/doctor/appointment
    
    Args:
        file_path: Path to data file
        prefix: Prefix for ID (e.g., 'P', 'D', 'A')
        
    Returns:
        Next ID string
    """
    data = load_json_file(file_path)
    count = len(data)
    next_id = f"{prefix}{count + 1:04d}"
    return next_id


def get_time_from_slot(slot_number):
    """
    Convert slot number to time string
    
    Args:
        slot_number: Slot number (0-based)
        
    Returns:
        Time string in HH:MM format
    """
    from config import DOCTOR_START_TIME, SLOT_DURATION
    
    total_minutes = slot_number * SLOT_DURATION
    hours = DOCTOR_START_TIME + (total_minutes // 60)
    minutes = total_minutes % 60
    
    return f"{hours:02d}:{minutes:02d}"


def clear_screen():
    """Clear console screen"""
    os.system('clear' if os.name == 'posix' else 'cls')


def print_separator(char="=", length=80):
    """Print separator line"""
    print(char * length)


def print_menu(title, options):
    """
    Print a formatted menu
    
    Args:
        title: Menu title
        options: List of option strings
    """
    print_separator()
    print(f"\n{'='*20} {title} {'='*20}\n")
    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option}")
    print()


def input_choice(prompt, valid_options):
    """
    Get user choice with validation
    
    Args:
        prompt: Input prompt
        valid_options: List of valid choices
        
    Returns:
        User's valid choice
    """
    while True:
        choice = input(prompt).strip()
        if choice in valid_options:
            return choice
        print(f"Invalid choice. Please select from {valid_options}")


def generate_diagnostic_report(patient_id, report_data):
    """
    Generate diagnostic report for patient
    
    Args:
        patient_id: Patient ID
        report_data: Report data dictionary
    """
    from config import REPORTS_DIR
    
    report_file = REPORTS_DIR / f"report_{patient_id}.json"
    
    try:
        # Load existing reports if any
        if report_file.exists():
            with open(report_file, 'r') as f:
                reports = json.load(f)
        else:
            reports = []
        
        # Add new report
        report_data['timestamp'] = datetime.now().isoformat()
        reports.append(report_data)
        
        # Save
        with open(report_file, 'w') as f:
            json.dump(reports, f, indent=4)
        
        logger.info(f"Generated diagnostic report for patient {patient_id}")
        
    except Exception as e:
        logger.error(f"Error generating diagnostic report for {patient_id}: {str(e)}")
