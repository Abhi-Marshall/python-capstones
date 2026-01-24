"""
Patient Class for Hospital Appointment Management System
"""

import threading
import json
from datetime import datetime
from utils import get_logger, load_json_file, save_json_file, get_next_id
from config import PATIENT_DATA_FILE

logger = get_logger(__name__)


class Patient:
    """
    Patient class to manage patient information
    """
    
    # Class-level lock for thread safety
    _lock = threading.Lock()
    
    def __init__(self, patient_id=None, name=None, age=None, contact=None):
        """
        Initialize Patient
        
        Args:
            patient_id: Unique patient ID
            name: Patient name
            age: Patient age
            contact: Contact number
        """
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.contact = contact
        self.thread_id = threading.current_thread().ident
        self.thread_name = threading.current_thread().name
        self.created_at = datetime.now().isoformat()
        
        logger.info(f"Patient object initialized: ID={self.patient_id}, Name={self.name}, ThreadID={self.thread_id}")
    
    def store_detail(self):
        """
        Store patient information to JSON file
        Uses thread-safe operation with lock
        """
        with Patient._lock:
            try:
                patients = load_json_file(PATIENT_DATA_FILE)
                
                patient_data = {
                    "name": self.name,
                    "age": self.age,
                    "contact": self.contact,
                    "thread_id": self.thread_id,
                    "thread_name": self.thread_name,
                    "created_at": self.created_at,
                    "status": "active"
                }
                
                patients[self.patient_id] = patient_data
                save_json_file(PATIENT_DATA_FILE, patients)
                
                logger.info(f"Patient {self.patient_id} ({self.name}) stored successfully")
                return True
                
            except Exception as e:
                logger.error(f"Error storing patient {self.patient_id}: {str(e)}")
                return False
    
    def display(self):
        """
        Display patient information
        """
        try:
            print("\n" + "="*60)
            print(f"{'PATIENT INFORMATION':^60}")
            print("="*60)
            print(f"Patient ID    : {self.patient_id}")
            print(f"Name          : {self.name}")
            print(f"Age           : {self.age}")
            print(f"Contact       : {self.contact}")
            print(f"Thread ID     : {self.thread_id}")
            print(f"Thread Name   : {self.thread_name}")
            print(f"Created At    : {self.created_at}")
            print("="*60 + "\n")
            
            logger.info(f"Displayed patient information for {self.patient_id}")
            
        except Exception as e:
            logger.error(f"Error displaying patient information: {str(e)}")
    
    @staticmethod
    def create_new_patient():
        """
        Interactive method to create a new patient
        
        Returns:
            Patient object if successful, None otherwise
        """
        try:
            print("\n" + "="*60)
            print(f"{'PATIENT REGISTRATION':^60}")
            print("="*60)
            
            name = input("Enter Patient Name: ").strip()
            while not name:
                print("Name cannot be empty!")
                name = input("Enter Patient Name: ").strip()
            
            age = input("Enter Patient Age: ").strip()
            while not age.isdigit() or int(age) <= 0:
                print("Please enter a valid age!")
                age = input("Enter Patient Age: ").strip()
            
            contact = input("Enter Contact Number: ").strip()
            while not contact or len(contact) < 10:
                print("Please enter a valid contact number!")
                contact = input("Enter Contact Number: ").strip()
            
            # Generate patient ID
            patient_id = get_next_id(PATIENT_DATA_FILE, "P")
            
            # Create patient object
            patient = Patient(
                patient_id=patient_id,
                name=name,
                age=int(age),
                contact=contact
            )
            
            # Store in database
            if patient.store_detail():
                print(f"\n✓ Patient registered successfully with ID: {patient_id}")
                logger.info(f"New patient created: {patient_id} - {name}")
                return patient
            else:
                print("\n✗ Error registering patient")
                logger.error(f"Failed to create patient: {name}")
                return None
            
        except Exception as e:
            print(f"\n✗ Error creating patient: {str(e)}")
            logger.error(f"Exception in create_new_patient: {str(e)}")
            return None
    
    @staticmethod
    def load_patient(patient_id):
        """
        Load patient from JSON file
        
        Args:
            patient_id: Patient ID to load
            
        Returns:
            Patient object if found, None otherwise
        """
        try:
            patients = load_json_file(PATIENT_DATA_FILE)
            
            if patient_id not in patients:
                logger.warning(f"Patient {patient_id} not found")
                return None
            
            patient_data = patients[patient_id]
            patient = Patient(
                patient_id=patient_id,
                name=patient_data.get("name"),
                age=patient_data.get("age"),
                contact=patient_data.get("contact")
            )
            
            patient.created_at = patient_data.get("created_at", patient.created_at)
            logger.info(f"Loaded patient {patient_id} from database")
            return patient
            
        except Exception as e:
            logger.error(f"Error loading patient {patient_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_all_patients():
        """
        Get all patients
        
        Returns:
            Dictionary of all patients
        """
        try:
            patients = load_json_file(PATIENT_DATA_FILE)
            logger.info(f"Retrieved {len(patients)} patients from database")
            return patients
        except Exception as e:
            logger.error(f"Error retrieving patients: {str(e)}")
            return {}
