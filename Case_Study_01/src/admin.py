"""
Admin Thread Handler for Hospital Appointment Management System
Controls the global counter (timestamp simulation) and generates diagnostic reports
"""

import threading
import time
import json
from datetime import datetime
from utils import get_logger, load_json_file, save_json_file, generate_diagnostic_report
from config import APPOINTMENT_DATA_FILE, DOCTOR_DATA_FILE, PATIENT_DATA_FILE

logger = get_logger(__name__)


class AdminThread(threading.Thread):
    """
    Admin thread that controls the global counter and simulates time
    Generates diagnostic reports every 30 minutes (slot completion)
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        """Initialize Admin Thread"""
        super().__init__(name="AdminThread", daemon=True)
        self.counter = 0  # Global counter (each increment = 30 min)
        self.running = True
        self.max_slots = 16  # 16 slots from 10 AM to 6 PM (30-min intervals)
        self.appointment_counter = 0
        
        logger.info("Admin Thread initialized")
    
    @staticmethod
    def get_instance():
        """
        Singleton pattern to ensure only one admin thread exists
        
        Returns:
            AdminThread instance
        """
        if AdminThread._instance is None:
            with AdminThread._lock:
                if AdminThread._instance is None:
                    AdminThread._instance = AdminThread()
        
        return AdminThread._instance
    
    def increment_counter(self):
        """
        Increment the global counter (30-minute increment)
        Each increment represents completion of a slot
        """
        self.counter += 1
        self.counter = self.counter % self.max_slots  # Reset after 16 slots
        
        logger.info(f"Admin counter incremented to {self.counter} (Slot: {self.counter})")
        
        # Generate diagnostic report for completed appointment
        self._generate_slot_report()
    
    def _generate_slot_report(self):
        """
        Generate diagnostic report when a slot is completed
        """
        try:
            appointments = load_json_file(APPOINTMENT_DATA_FILE)
            
            # Find appointment for current slot
            for apt_id, apt_data in appointments.items():
                if apt_data.get("status") == "confirmed":
                    patient_id = apt_data.get("patient_id")
                    doctor_id = apt_data.get("doctor_id")
                    slot_id = apt_data.get("slot_id")
                    
                    # Check if this appointment matches current counter
                    if self.counter == slot_id:
                        report_data = {
                            "appointment_id": apt_id,
                            "patient_id": patient_id,
                            "doctor_id": doctor_id,
                            "slot_id": slot_id,
                            "timestamp": datetime.now().isoformat(),
                            "consultation_notes": f"Consultation completed at slot {slot_id}",
                            "vitals": {
                                "blood_pressure": "120/80",
                                "heart_rate": "72 bpm",
                                "temperature": "98.6°F"
                            },
                            "diagnosis": "Routine checkup completed",
                            "prescription": "Take rest and maintain healthy diet",
                            "follow_up": "After 3 months"
                        }
                        
                        generate_diagnostic_report(patient_id, report_data)
                        
                        logger.info(f"Generated diagnostic report for patient {patient_id} at slot {self.counter}")
        
        except Exception as e:
            logger.error(f"Error generating slot report: {str(e)}")
    
    def get_current_slot(self):
        """
        Get current slot number
        
        Returns:
            Current slot number
        """
        return self.counter
    
    def get_status(self):
        """
        Get admin thread status
        
        Returns:
            Dictionary with status information
        """
        from config import DOCTOR_START_TIME, SLOT_DURATION
        
        total_minutes = self.counter * SLOT_DURATION
        hours = DOCTOR_START_TIME + (total_minutes // 60)
        minutes = total_minutes % 60
        current_time = f"{hours:02d}:{minutes:02d}"
        
        return {
            "counter": self.counter,
            "current_slot": self.counter,
            "simulated_time": current_time,
            "running": self.running
        }
    
    def run(self):
        """
        Admin thread main loop
        Runs continuously and increments counter periodically
        """
        logger.info("Admin Thread started")
        
        try:
            while self.running:
                time.sleep(5)  # Increment counter every 5 seconds for demo
                # In production, this could be scheduled differently
        
        except Exception as e:
            logger.error(f"Error in Admin Thread: {str(e)}")
        
        finally:
            logger.info("Admin Thread stopped")
    
    def stop(self):
        """Stop the admin thread"""
        self.running = False
        logger.info("Admin Thread stop signal sent")
    
    def display_status(self):
        """Display admin thread status"""
        status = self.get_status()
        
        print("\n" + "="*70)
        print(f"{'ADMIN PANEL - SYSTEM STATUS':^70}")
        print("="*70)
        print(f"Counter (Slot)        : {status['counter']}")
        print(f"Simulated Time        : {status['simulated_time']}")
        print(f"Thread Status         : {'RUNNING' if status['running'] else 'STOPPED'}")
        print("="*70 + "\n")


class TimeSimulation:
    """
    Helper class to manage time simulation
    """
    
    @staticmethod
    def advance_time(slots=1):
        """
        Advance time by specified number of slots
        
        Args:
            slots: Number of slots to advance (default: 1)
        """
        admin = AdminThread.get_instance()
        
        for _ in range(slots):
            admin.increment_counter()
            time.sleep(0.5)
        
        logger.info(f"Time advanced by {slots} slots")
    
    @staticmethod
    def get_current_time():
        """
        Get current simulated time
        
        Returns:
            Time string in HH:MM format
        """
        admin = AdminThread.get_instance()
        return admin.get_status()['simulated_time']
    
    @staticmethod
    def reset_time():
        """Reset the global counter to 0 and reset all doctor slots"""
        try:
            from doctor import Doctor
            
            admin = AdminThread.get_instance()
            admin.counter = 0
            logger.info(f"Admin counter reset to {admin.counter}")
            
            # Reset all doctor slots to available
            result = Doctor.reset_all_slots()
            
            if result:
                logger.info("Time reset to 0 and all slots reset to available")
            else:
                logger.error("Failed to reset doctor slots")
        
        except Exception as e:
            logger.error(f"Error in reset_time: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
