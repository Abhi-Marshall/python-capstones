"""
Appointment Class for Hospital Appointment Management System
Inherits from both Patient and Doctor
"""

import threading
import json
from datetime import datetime
from patient import Patient
from doctor import Doctor
from utils import get_logger, load_json_file, save_json_file, get_next_id, generate_diagnostic_report
from config import APPOINTMENT_DATA_FILE, DEPARTMENTS

logger = get_logger(__name__)


class Appointment(Patient, Doctor):
    """
    Appointment class that inherits from Patient and Doctor
    Manages appointment bookings with thread safety
    """
    
    # Class-level locks for thread safety
    _lock = threading.Lock()
    _booking_locks = {}  # Per-slot locks
    
    def __init__(self, appointment_id=None, patient_id=None, doctor_id=None, slot_id=None):
        """
        Initialize Appointment
        
        Args:
            appointment_id: Unique appointment ID
            patient_id: Patient ID
            doctor_id: Doctor ID
            slot_id: Slot ID
        """
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.slot_id = slot_id
        self.thread_id = threading.current_thread().ident
        self.thread_name = threading.current_thread().name
        self.created_at = datetime.now().isoformat()
        self.status = "pending"
        self.confirmed = False
        
        logger.info(f"Appointment object initialized: ID={self.appointment_id}, Patient={self.patient_id}, Doctor={self.doctor_id}")
    
    def link_doctor_patient(self):
        """
        Interactive method to link doctor and patient for appointment
        
        Process:
        1. Patient chooses medical field
        2. Patient chooses doctor from available doctors
        3. Patient chooses available slot from doctor
        
        Returns:
            Appointment object if successful, None otherwise
        """
        try:
            print("\n" + "="*70)
            print(f"{'BOOK APPOINTMENT':^70}")
            print("="*70)
            
            # Step 1: Choose Department
            print("\nSelect Medical Department:")
            for key, dept in DEPARTMENTS.items():
                print(f"{key}. {dept}")
            
            dept_choice = input("\nEnter Department Choice (or 'b' to go back): ").strip()
            if dept_choice.lower() == 'b':
                return None
            
            if dept_choice not in DEPARTMENTS:
                print("✗ Invalid choice!")
                logger.warning(f"Invalid department choice: {dept_choice}")
                return None
            
            department = DEPARTMENTS[dept_choice]
            logger.info(f"Patient {self.patient_id} selected department: {department}")
            
            # Step 2: Choose Doctor from Department
            available_doctors = Doctor.get_doctors_by_department(department)
            
            if not available_doctors:
                print(f"\n✗ No doctors available in {department}")
                logger.warning(f"No doctors available in {department}")
                return None
            
            print(f"\n{'='*70}")
            print(f"Available Doctors in {department}:")
            print(f"{'='*70}")
            
            doctors_list = []
            for idx, doc_id in enumerate(available_doctors, 1):
                doctors = load_json_file(Doctor.DOCTOR_DATA_FILE if hasattr(Doctor, 'DOCTOR_DATA_FILE') else "/Users/as-mac-1233/Documents/hospital/data/doctor.json")
                if doc_id in doctors:
                    doc = doctors[doc_id]
                    print(f"{idx}. Dr. {doc['name']} - {doc['qualification']}")
                    doctors_list.append(doc_id)
            
            print(f"\n0. Go Back")
            
            doctor_choice = input("\nSelect Doctor (enter number): ").strip()
            if doctor_choice == '0':
                return None
            
            try:
                doctor_idx = int(doctor_choice) - 1
                if 0 <= doctor_idx < len(doctors_list):
                    self.doctor_id = doctors_list[doctor_idx]
                    logger.info(f"Patient {self.patient_id} selected doctor: {self.doctor_id}")
                else:
                    print("✗ Invalid choice!")
                    return None
            except ValueError:
                print("✗ Invalid input!")
                return None
            
            # Step 3: Load Doctor and show available slots
            doctor = Doctor.load_doctor(self.doctor_id)
            if not doctor:
                print("✗ Error loading doctor information")
                return None
            
            available_slots = doctor.display_slots()
            
            if not available_slots:
                print("✗ No available slots for this doctor")
                logger.warning(f"No available slots for doctor {self.doctor_id}")
                return None
            
            print("\nSelect Slot:")
            for slot in available_slots:
                print(f"{slot['slot_id']}. {slot['time']}")
            
            print(f"\n0. Go Back")
            
            slot_choice = input("\nSelect Slot (enter number or 0 to go back): ").strip()
            if slot_choice == '0':
                return None
            
            try:
                self.slot_id = int(slot_choice)
                
                # Validate slot
                if self.slot_id < 0 or self.slot_id >= len(doctor.available_slots):
                    print("✗ Invalid slot!")
                    return None
                
                if doctor.available_slots[self.slot_id]["booked"]:
                    print("✗ Selected slot is already booked!")
                    logger.warning(f"Patient {self.patient_id} tried to book already booked slot")
                    return None
                
                logger.info(f"Patient {self.patient_id} selected slot {self.slot_id} for doctor {self.doctor_id}")
                
            except ValueError:
                print("✗ Invalid input!")
                return None
            
            return self
            
        except Exception as e:
            print(f"\n✗ Error linking doctor and patient: {str(e)}")
            logger.error(f"Exception in link_doctor_patient: {str(e)}")
            return None
    
    def confirm_booking(self):
        """
        Confirm appointment booking with lock mechanism
        Ensures thread-safe slot booking
        
        Returns:
            True if booking confirmed, False otherwise
        """
        try:
            # Get or create per-slot lock
            slot_key = f"{self.doctor_id}_{self.slot_id}"
            
            with Appointment._lock:
                if slot_key not in Appointment._booking_locks:
                    Appointment._booking_locks[slot_key] = threading.Lock()
                slot_lock = Appointment._booking_locks[slot_key]
            
            # Acquire slot-specific lock for booking
            with slot_lock:
                logger.info(f"Booking confirmation thread acquired lock for slot {slot_key}")
                
                # Reload doctor to check current slot status
                doctor = Doctor.load_doctor(self.doctor_id)
                if not doctor:
                    logger.error(f"Cannot load doctor {self.doctor_id}")
                    return False
                
                # Check if slot is still available
                if doctor.available_slots[self.slot_id]["booked"]:
                    print(f"\n✗ Slot is no longer available! (Another patient just booked it)")
                    logger.warning(f"Slot {self.slot_id} already booked before confirmation")
                    return False
                
                # Book the slot
                if not doctor.reduce_slots(self.slot_id, self.patient_id):
                    logger.error(f"Failed to book slot {self.slot_id}")
                    return False
                
                # Store appointment
                appointments = load_json_file(APPOINTMENT_DATA_FILE)
                appointment_data = {
                    "patient_id": self.patient_id,
                    "doctor_id": self.doctor_id,
                    "slot_id": self.slot_id,
                    "appointment_time": doctor.available_slots[self.slot_id]["time"],
                    "status": "confirmed",
                    "created_at": self.created_at,
                    "confirmed_at": datetime.now().isoformat(),
                    "thread_id": self.thread_id,
                    "thread_name": self.thread_name
                }
                
                self.appointment_id = get_next_id(APPOINTMENT_DATA_FILE, "A")
                appointments[self.appointment_id] = appointment_data
                save_json_file(APPOINTMENT_DATA_FILE, appointments)
                
                # Update doctor's slots in database
                doctor.store_detail()
                
                print(f"\n✓ Appointment confirmed successfully!")
                print(f"✓ Appointment ID: {self.appointment_id}")
                print(f"✓ Slot: {doctor.available_slots[self.slot_id]['time']}")
                
                self.confirmed = True
                self.status = "confirmed"
                
                logger.info(f"Appointment {self.appointment_id} confirmed for patient {self.patient_id}")
                
                return True
                
        except Exception as e:
            print(f"\n✗ Error confirming booking: {str(e)}")
            logger.error(f"Exception in confirm_booking: {str(e)}")
            return False
    
    def display(self):
        """
        Display appointment information
        """
        try:
            doctor_data = load_json_file("/Users/as-mac-1233/Documents/hospital/data/doctor.json")
            patient_data = load_json_file("/Users/as-mac-1233/Documents/hospital/data/patient.json")
            
            doctor_info = doctor_data.get(self.doctor_id, {})
            patient_info = patient_data.get(self.patient_id, {})
            
            print("\n" + "="*70)
            print(f"{'APPOINTMENT INFORMATION':^70}")
            print("="*70)
            print(f"Appointment ID  : {self.appointment_id}")
            print(f"Patient ID      : {self.patient_id} ({patient_info.get('name', 'N/A')})")
            print(f"Doctor ID       : {self.doctor_id} ({doctor_info.get('name', 'N/A')})")
            print(f"Department      : {doctor_info.get('department', 'N/A')}")
            print(f"Slot ID         : {self.slot_id}")
            
            if self.appointment_id and self.appointment_id in load_json_file(APPOINTMENT_DATA_FILE):
                apt_data = load_json_file(APPOINTMENT_DATA_FILE)[self.appointment_id]
                print(f"Appointment Time: {apt_data.get('appointment_time', 'N/A')}")
            
            print(f"Status          : {self.status}")
            print(f"Created At      : {self.created_at}")
            print("="*70 + "\n")
            
            logger.info(f"Displayed appointment information for {self.appointment_id}")
            
        except Exception as e:
            logger.error(f"Error displaying appointment information: {str(e)}")
    
    @staticmethod
    def load_appointment(appointment_id):
        """
        Load appointment from JSON file
        
        Args:
            appointment_id: Appointment ID to load
            
        Returns:
            Appointment object if found, None otherwise
        """
        try:
            appointments = load_json_file(APPOINTMENT_DATA_FILE)
            
            if appointment_id not in appointments:
                logger.warning(f"Appointment {appointment_id} not found")
                return None
            
            apt_data = appointments[appointment_id]
            appointment = Appointment(
                appointment_id=appointment_id,
                patient_id=apt_data.get("patient_id"),
                doctor_id=apt_data.get("doctor_id"),
                slot_id=apt_data.get("slot_id")
            )
            
            appointment.status = apt_data.get("status", "pending")
            appointment.confirmed = apt_data.get("status") == "confirmed"
            appointment.created_at = apt_data.get("created_at", appointment.created_at)
            
            logger.info(f"Loaded appointment {appointment_id} from database")
            return appointment
            
        except Exception as e:
            logger.error(f"Error loading appointment {appointment_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_all_appointments():
        """
        Get all appointments
        
        Returns:
            Dictionary of all appointments
        """
        try:
            appointments = load_json_file(APPOINTMENT_DATA_FILE)
            logger.info(f"Retrieved {len(appointments)} appointments from database")
            return appointments
        except Exception as e:
            logger.error(f"Error retrieving appointments: {str(e)}")
            return {}
