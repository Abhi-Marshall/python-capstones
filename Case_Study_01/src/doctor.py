"""
Doctor Class for Hospital Appointment Management System
"""

import threading
import json
from datetime import datetime
from utils import get_logger, load_json_file, save_json_file, get_next_id, get_time_from_slot
from config import DOCTOR_DATA_FILE, DOCTOR_START_TIME, DOCTOR_END_TIME, TOTAL_SLOTS_PER_DAY

logger = get_logger(__name__)


class Doctor:
    """
    Doctor class to manage doctor information and appointment slots
    """
    
    # Class-level lock for thread safety
    _lock = threading.Lock()
    
    # Global dictionary to store doctor slots
    _doctors_global = {}
    
    def __init__(self, doctor_id=None, name=None, department=None, qualification=None):
        """
        Initialize Doctor
        
        Args:
            doctor_id: Unique doctor ID
            name: Doctor name
            department: Medical department
            qualification: Doctor's qualification
        """
        self.doctor_id = doctor_id
        self.name = name
        self.department = department
        self.qualification = qualification
        self.thread_id = threading.current_thread().ident
        self.thread_name = threading.current_thread().name
        self.created_at = datetime.now().isoformat()
        self.available_slots = self._initialize_slots()
        
        logger.info(f"Doctor object initialized: ID={self.doctor_id}, Name={self.name}, Dept={self.department}")
    
    def _initialize_slots(self):
        """
        Initialize available slots for the doctor
        
        Returns:
            List of available slots (10 AM to 6 PM, 30-min intervals)
        """
        slots = []
        for i in range(TOTAL_SLOTS_PER_DAY):
            slots.append({
                "slot_id": i,
                "time": get_time_from_slot(i),
                "booked": False,
                "booked_by": None,
                "booked_at": None
            })
        return slots
    
    def display_slots(self):
        """
        Display available slots for the doctor
        
        Returns:
            List of available slots
        """
        try:
            available = [slot for slot in self.available_slots if not slot["booked"]]
            
            print("\n" + "="*70)
            print(f"{'AVAILABLE SLOTS - Dr. ' + self.name:^70}")
            print(f"{'Department: ' + self.department:^70}")
            print("="*70)
            print(f"{'Slot#':<10} {'Time':<15} {'Status':<20}")
            print("-"*70)
            
            for slot in self.available_slots:
                status = "BOOKED" if slot["booked"] else "AVAILABLE"
                slot_color = "✓" if status == "BOOKED" else "◇"
                print(f"{slot_color} {slot['slot_id']:<8} {slot['time']:<15} {status:<20}")
            
            print("="*70 + "\n")
            logger.info(f"Displayed available slots for doctor {self.doctor_id}")
            
            return available
            
        except Exception as e:
            logger.error(f"Error displaying available slots: {str(e)}")
            return []
    
    def reduce_slots(self, slot_id, patient_id):
        """
        Book a slot for a patient (reduce available slots)
        Uses lock for thread safety
        
        Args:
            slot_id: Slot ID to book
            patient_id: Patient ID booking the slot
            
        Returns:
            True if successful, False otherwise
        """
        with Doctor._lock:
            try:
                # Check if slot is valid and available
                if slot_id < 0 or slot_id >= len(self.available_slots):
                    logger.warning(f"Invalid slot ID: {slot_id}")
                    return False
                
                slot = self.available_slots[slot_id]
                
                if slot["booked"]:
                    logger.warning(f"Slot {slot_id} already booked by {slot['booked_by']}")
                    print(f"\n✗ This slot is already booked!")
                    return False
                
                # Book the slot
                slot["booked"] = True
                slot["booked_by"] = patient_id
                slot["booked_at"] = datetime.now().isoformat()
                
                logger.info(f"Slot {slot_id} booked by patient {patient_id} for doctor {self.doctor_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error booking slot {slot_id}: {str(e)}")
                return False
    
    def display(self):
        """
        Display doctor information
        """
        try:
            print("\n" + "="*60)
            print(f"{'DOCTOR INFORMATION':^60}")
            print("="*60)
            print(f"Doctor ID      : {self.doctor_id}")
            print(f"Name           : {self.name}")
            print(f"Department     : {self.department}")
            print(f"Qualification  : {self.qualification}")
            print(f"Thread ID      : {self.thread_id}")
            print(f"Thread Name    : {self.thread_name}")
            print(f"Created At     : {self.created_at}")
            print("="*60 + "\n")
            
            logger.info(f"Displayed doctor information for {self.doctor_id}")
            
        except Exception as e:
            logger.error(f"Error displaying doctor information: {str(e)}")
    
    def store_detail(self):
        """
        Store doctor information to JSON file with slots
        Uses thread-safe operation with lock
        """
        with Doctor._lock:
            try:
                doctors = load_json_file(DOCTOR_DATA_FILE)
                
                doctor_data = {
                    "name": self.name,
                    "department": self.department,
                    "qualification": self.qualification,
                    "thread_id": self.thread_id,
                    "thread_name": self.thread_name,
                    "created_at": self.created_at,
                    "available_slots": self.available_slots,
                    "status": "active"
                }
                
                doctors[self.doctor_id] = doctor_data
                save_json_file(DOCTOR_DATA_FILE, doctors)
                
                # Also store in global dictionary
                Doctor._doctors_global[self.doctor_id] = self
                
                logger.info(f"Doctor {self.doctor_id} ({self.name}) stored successfully")
                return True
                
            except Exception as e:
                logger.error(f"Error storing doctor {self.doctor_id}: {str(e)}")
                return False
    
    @staticmethod
    def create_new_doctor():
        """
        Interactive method to create a new doctor
        
        Returns:
            Doctor object if successful, None otherwise
        """
        from config import DEPARTMENTS
        
        try:
            print("\n" + "="*60)
            print(f"{'DOCTOR REGISTRATION':^60}")
            print("="*60)
            
            name = input("Enter Doctor Name: ").strip()
            while not name:
                print("Name cannot be empty!")
                name = input("Enter Doctor Name: ").strip()
            
            print("\nSelect Department:")
            for key, dept in DEPARTMENTS.items():
                print(f"{key}. {dept}")
            
            dept_choice = input("Enter Department Choice: ").strip()
            while dept_choice not in DEPARTMENTS:
                print("Invalid choice!")
                dept_choice = input("Enter Department Choice: ").strip()
            
            department = DEPARTMENTS[dept_choice]
            
            qualification = input("Enter Qualification (e.g., MD, MBBS): ").strip()
            while not qualification:
                print("Qualification cannot be empty!")
                qualification = input("Enter Qualification: ").strip()
            
            # Generate doctor ID
            doctor_id = get_next_id(DOCTOR_DATA_FILE, "D")
            
            # Create doctor object
            doctor = Doctor(
                doctor_id=doctor_id,
                name=name,
                department=department,
                qualification=qualification
            )
            
            # Store in database
            if doctor.store_detail():
                print(f"\n✓ Doctor registered successfully with ID: {doctor_id}")
                logger.info(f"New doctor created: {doctor_id} - {name} in {department}")
                return doctor
            else:
                print("\n✗ Error registering doctor")
                logger.error(f"Failed to create doctor: {name}")
                return None
            
        except Exception as e:
            print(f"\n✗ Error creating doctor: {str(e)}")
            logger.error(f"Exception in create_new_doctor: {str(e)}")
            return None
    
    @staticmethod
    def load_doctor(doctor_id):
        """
        Load doctor from JSON file
        
        Args:
            doctor_id: Doctor ID to load
            
        Returns:
            Doctor object if found, None otherwise
        """
        try:
            doctors = load_json_file(DOCTOR_DATA_FILE)
            
            if doctor_id not in doctors:
                logger.warning(f"Doctor {doctor_id} not found")
                return None
            
            doctor_data = doctors[doctor_id]
            doctor = Doctor(
                doctor_id=doctor_id,
                name=doctor_data.get("name"),
                department=doctor_data.get("department"),
                qualification=doctor_data.get("qualification")
            )
            
            # Restore slots
            if "available_slots" in doctor_data:
                doctor.available_slots = doctor_data["available_slots"]
            
            doctor.created_at = doctor_data.get("created_at", doctor.created_at)
            Doctor._doctors_global[doctor_id] = doctor
            
            logger.info(f"Loaded doctor {doctor_id} from database")
            return doctor
            
        except Exception as e:
            logger.error(f"Error loading doctor {doctor_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_all_doctors():
        """
        Get all doctors
        
        Returns:
            Dictionary of all doctors
        """
        try:
            doctors = load_json_file(DOCTOR_DATA_FILE)
            logger.info(f"Retrieved {len(doctors)} doctors from database")
            return doctors
        except Exception as e:
            logger.error(f"Error retrieving doctors: {str(e)}")
            return {}
    
    @staticmethod
    def get_doctors_by_department(department):
        """
        Get all doctors in a specific department
        
        Args:
            department: Department name
            
        Returns:
            List of doctor IDs
        """
        try:
            all_doctors = Doctor.get_all_doctors()
            doctors_in_dept = [
                doc_id for doc_id, doc_data in all_doctors.items()
                if doc_data.get("department") == department
            ]
            logger.info(f"Retrieved {len(doctors_in_dept)} doctors from {department}")
            return doctors_in_dept
        except Exception as e:
            logger.error(f"Error retrieving doctors by department: {str(e)}")
            return []
    
    @staticmethod
    def reset_all_slots():
        """
        Reset all doctor slots to available (unbooked status)
        Called when admin resets the system time
        
        Returns:
            True if successful, False otherwise
        """
        try:
            doctors = load_json_file(DOCTOR_DATA_FILE)
            
            for doc_id, doc_data in doctors.items():
                # Reset all slots for this doctor to unbooked
                if "available_slots" in doc_data:
                    for slot in doc_data["available_slots"]:
                        slot["booked"] = False
                        slot["booked_by"] = None
                        slot["booked_at"] = None
            
            # Save the updated doctors data
            save_json_file(DOCTOR_DATA_FILE, doctors)
            logger.info("All doctor slots reset to available")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting doctor slots: {str(e)}")
            return False
