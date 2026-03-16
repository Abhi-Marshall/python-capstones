"""
Menu Interface for Hospital Appointment Management System
Provides interactive menu-based navigation
"""

import os
import threading
from utils import get_logger, clear_screen, print_separator, print_menu, input_choice
from patient import Patient
from doctor import Doctor
from appointment import Appointment
from admin import AdminThread, TimeSimulation

logger = get_logger(__name__)


class MenuInterface:
    """
    Main menu interface for the hospital system
    """
    
    def __init__(self):
        """Initialize Menu Interface"""
        self.current_patient = None
        self.admin_thread = AdminThread.get_instance()
        logger.info("Menu Interface initialized")
    
    def main_menu(self):
        """
        Display main menu
        """
        while True:
            clear_screen()
            print_separator("=", 80)
            print(f"\n{'HOSPITAL APPOINTMENT MANAGEMENT SYSTEM':^80}\n")
            print_separator("=", 80)
            
            print("\nMAIN MENU\n")
            options = [
                "Patient Portal",
                "Doctor Portal",
                "Admin Panel",
                "View System Status",
                "Exit"
            ]
            
            for idx, option in enumerate(options, 1):
                print(f"{idx}. {option}")
            
            choice = input("\nSelect Option (1-5): ").strip()
            
            if choice == '1':
                self.patient_portal()
            elif choice == '2':
                self.doctor_portal()
            elif choice == '3':
                self.admin_panel()
            elif choice == '4':
                self.view_system_status()
            elif choice == '5':
                self.exit_system()
                break
            else:
                print("\n✗ Invalid choice! Press Enter to continue...")
                input()
    
    def patient_portal(self):
        """
        Patient portal menu
        """
        while True:
            clear_screen()
            print_separator()
            print(f"\n{'PATIENT PORTAL':^80}\n")
            print_separator()
            
            print("\nPATIENT MENU\n")
            options = [
                "Register New Patient",
                "Login as Existing Patient",
                "View Patient Information",
                "Book Appointment",
                "View My Appointments",
                "View Diagnostic Report",
                "Back to Main Menu"
            ]
            
            for idx, option in enumerate(options, 1):
                print(f"{idx}. {option}")
            
            choice = input("\nSelect Option (1-7): ").strip()
            
            if choice == '1':
                self.register_patient()
            elif choice == '2':
                self.login_patient()
            elif choice == '3':
                self.view_patient_info()
            elif choice == '4':
                self.book_appointment_menu()
            elif choice == '5':
                self.view_patient_appointments()
            elif choice == '6':
                self.view_diagnostic_report()
            elif choice == '7':
                break
            else:
                print("\n✗ Invalid choice! Press Enter to continue...")
                input()
    
    def register_patient(self):
        """Register a new patient"""
        clear_screen()
        print("\n")
        patient = Patient.create_new_patient()
        
        if patient:
            input("\n✓ Press Enter to continue...")
            logger.info(f"Patient {patient.patient_id} registered through menu")
        else:
            input("\n✗ Press Enter to continue...")
    
    def login_patient(self):
        """Login as existing patient"""
        clear_screen()
        
        patient_id = input("\nEnter Patient ID (or 'b' to go back): ").strip()
        
        if patient_id.lower() == 'b':
            return
        
        patient = Patient.load_patient(patient_id)
        
        if patient:
            self.current_patient = patient
            print(f"\n✓ Welcome, {patient.name}!")
            patient.display()
            input("Press Enter to continue...")
            logger.info(f"Patient {patient_id} logged in")
        else:
            print(f"\n✗ Patient {patient_id} not found!")
            input("Press Enter to continue...")
    
    def view_patient_info(self):
        """View current patient information"""
        clear_screen()
        
        if not self.current_patient:
            print("\n✗ No patient logged in!")
            input("Press Enter to continue...")
            return
        
        self.current_patient.display()
        input("Press Enter to continue...")
    
    def book_appointment_menu(self):
        """Menu for booking appointment"""
        clear_screen()
        
        if not self.current_patient:
            print("\n✗ Please login first!")
            input("Press Enter to continue...")
            return
        
        print("\n" + "="*70)
        print(f"{'BOOK APPOINTMENT FOR: ' + self.current_patient.name:^70}")
        print("="*70)
        
        # Create appointment object
        appointment = Appointment(patient_id=self.current_patient.patient_id)
        
        # Link doctor and patient
        result = appointment.link_doctor_patient()
        
        if result:
            print("\n" + "="*70)
            confirm = input("Confirm Booking? (Press 'y' to confirm, 'n' to cancel): ").strip().lower()
            
            if confirm == 'y':
                # Start patient thread for booking
                patient_thread = threading.Thread(
                    target=self._patient_booking_thread,
                    args=(appointment,),
                    name=f"PatientThread-{self.current_patient.patient_id}"
                )
                patient_thread.start()
                patient_thread.join()  # Wait for thread to complete
            else:
                print("\n✗ Booking cancelled!")
                logger.info(f"Booking cancelled by patient {self.current_patient.patient_id}")
        
        input("\nPress Enter to continue...")
    
    def _patient_booking_thread(self, appointment):
        """
        Patient booking thread function
        
        Args:
            appointment: Appointment object to book
        """
        logger.info(f"Patient booking thread started for {appointment.patient_id}")
        
        # Simulate doctor thread
        doctor_thread = threading.Thread(
            target=self._doctor_booking_thread,
            args=(appointment,),
            name=f"DoctorThread-{appointment.doctor_id}"
        )
        doctor_thread.start()
        
        # Confirm booking
        appointment.confirm_booking()
        
        # Wait for doctor thread
        doctor_thread.join()
        
        logger.info(f"Patient booking thread completed for {appointment.patient_id}")
    
    def _doctor_booking_thread(self, appointment):
        """
        Doctor booking thread function (simulated)
        
        Args:
            appointment: Appointment object
        """
        logger.info(f"Doctor thread started for doctor {appointment.doctor_id}")
        import time
        time.sleep(0.5)  # Simulate some work
        logger.info(f"Doctor thread completed for doctor {appointment.doctor_id}")
    
    def view_patient_appointments(self):
        """View patient's appointments"""
        clear_screen()
        
        if not self.current_patient:
            print("\n✗ Please login first!")
            input("Press Enter to continue...")
            return
        
        from utils import load_json_file
        from config import APPOINTMENT_DATA_FILE
        
        appointments = load_json_file(APPOINTMENT_DATA_FILE)
        patient_apts = {
            apt_id: apt_data for apt_id, apt_data in appointments.items()
            if apt_data.get("patient_id") == self.current_patient.patient_id
        }
        
        clear_screen()
        print("\n" + "="*70)
        print(f"{'YOUR APPOINTMENTS':^70}")
        print("="*70)
        
        if not patient_apts:
            print("\nNo appointments found.")
        else:
            print(f"\n{'Appointment ID':<15} {'Doctor ID':<15} {'Slot':<10} {'Time':<10} {'Status':<15}")
            print("-"*70)
            
            for apt_id, apt_data in patient_apts.items():
                print(f"{apt_id:<15} {apt_data.get('doctor_id', 'N/A'):<15} {apt_data.get('slot_id', 'N/A'):<10} {apt_data.get('appointment_time', 'N/A'):<10} {apt_data.get('status', 'N/A'):<15}")
        
        print("="*70 + "\n")
        input("Press Enter to continue...")
    
    def view_diagnostic_report(self):
        """View diagnostic report based on appointment ID"""
        clear_screen()
        
        if not self.current_patient:
            print("\n✗ Please login first!")
            input("Press Enter to continue...")
            return
        
        from utils import load_json_file
        from config import APPOINTMENT_DATA_FILE, REPORTS_DIR
        
        # Show patient's appointments first
        appointments = load_json_file(APPOINTMENT_DATA_FILE)
        patient_apts = {
            apt_id: apt_data for apt_id, apt_data in appointments.items()
            if apt_data.get("patient_id") == self.current_patient.patient_id
        }
        
        if not patient_apts:
            print("\n✗ No appointments found.")
            input("Press Enter to continue...")
            return
        
        print("\n" + "="*70)
        print(f"{'YOUR APPOINTMENTS':^70}")
        print("="*70)
        print(f"\n{'Appointment ID':<15} {'Doctor ID':<15} {'Slot':<10} {'Status':<15}")
        print("-"*70)
        
        for apt_id, apt_data in patient_apts.items():
            print(f"{apt_id:<15} {apt_data.get('doctor_id', 'N/A'):<15} {apt_data.get('slot_id', 'N/A'):<10} {apt_data.get('status', 'N/A'):<15}")
        
        print("="*70 + "\n")
        
        apt_id = input("Enter Appointment ID to view diagnostic report (or 'b' to go back): ").strip()
        
        if apt_id.lower() == 'b':
            return
        
        if apt_id not in patient_apts:
            print(f"\n✗ Appointment {apt_id} not found or does not belong to you!")
            input("Press Enter to continue...")
            return
        
        # Load and display the diagnostic report
        report_file = REPORTS_DIR / f"report_{self.current_patient.patient_id}.json"
        
        if not report_file.exists():
            print(f"\n✗ No diagnostic reports found for patient {self.current_patient.patient_id}")
            input("Press Enter to continue...")
            return
        
        try:
            reports = load_json_file(report_file)
            
            # Find report for the selected appointment
            matching_report = None
            for report in reports:
                if report.get("appointment_id") == apt_id:
                    matching_report = report
                    break
            
            if not matching_report:
                print(f"\n✗ No diagnostic report found for appointment {apt_id}")
                input("Press Enter to continue...")
                return
            
            clear_screen()
            print("\n" + "="*70)
            print(f"{'DIAGNOSTIC REPORT':^70}")
            print("="*70)
            print(f"\nAppointment ID       : {matching_report.get('appointment_id', 'N/A')}")
            print(f"Patient ID           : {matching_report.get('patient_id', 'N/A')}")
            print(f"Doctor ID            : {matching_report.get('doctor_id', 'N/A')}")
            print(f"Slot ID              : {matching_report.get('slot_id', 'N/A')}")
            print(f"Timestamp            : {matching_report.get('timestamp', 'N/A')}")
            print(f"\nConsultation Notes   : {matching_report.get('consultation_notes', 'N/A')}")
            
            vitals = matching_report.get('vitals', {})
            print(f"\nVitals:")
            print(f"  Blood Pressure      : {vitals.get('blood_pressure', 'N/A')}")
            print(f"  Heart Rate          : {vitals.get('heart_rate', 'N/A')}")
            print(f"  Temperature         : {vitals.get('temperature', 'N/A')}")
            
            print(f"\nDiagnosis            : {matching_report.get('diagnosis', 'N/A')}")
            print(f"Prescription         : {matching_report.get('prescription', 'N/A')}")
            print(f"Follow-up            : {matching_report.get('follow_up', 'N/A')}")
            print("="*70 + "\n")
            
            logger.info(f"Patient {self.current_patient.patient_id} viewed diagnostic report for appointment {apt_id}")
            
        except Exception as e:
            print(f"\n✗ Error loading diagnostic report: {str(e)}")
            logger.error(f"Error viewing diagnostic report: {str(e)}")
        
        input("Press Enter to continue...")
    
    def doctor_portal(self):
        """
        Doctor portal menu
        """
        while True:
            clear_screen()
            print_separator()
            print(f"\n{'DOCTOR PORTAL':^80}\n")
            print_separator()
            
            print("\nDOCTOR MENU\n")
            options = [
                "Register New Doctor",
                "Login as Existing Doctor",
                "View Doctor Information",
                "View My Available Slots",
                "View My Appointments",
                "Back to Main Menu"
            ]
            
            for idx, option in enumerate(options, 1):
                print(f"{idx}. {option}")
            
            choice = input("\nSelect Option (1-6): ").strip()
            
            if choice == '1':
                self.register_doctor()
            elif choice == '2':
                self.login_doctor()
            elif choice == '3':
                self.view_doctor_info()
            elif choice == '4':
                self.view_doctor_slots()
            elif choice == '5':
                self.view_doctor_appointments()
            elif choice == '6':
                break
            else:
                print("\n✗ Invalid choice! Press Enter to continue...")
                input()
    
    def register_doctor(self):
        """Register a new doctor"""
        clear_screen()
        print("\n")
        doctor = Doctor.create_new_doctor()
        
        if doctor:
            input("\n✓ Press Enter to continue...")
            logger.info(f"Doctor {doctor.doctor_id} registered through menu")
        else:
            input("\n✗ Press Enter to continue...")
    
    def login_doctor(self):
        """Login as existing doctor"""
        clear_screen()
        
        doctor_id = input("\nEnter Doctor ID (or 'b' to go back): ").strip()
        
        if doctor_id.lower() == 'b':
            return
        
        doctor = Doctor.load_doctor(doctor_id)
        
        if doctor:
            print(f"\n✓ Welcome, Dr. {doctor.name}!")
            doctor.display()
            input("Press Enter to continue...")
            logger.info(f"Doctor {doctor_id} logged in")
        else:
            print(f"\n✗ Doctor {doctor_id} not found!")
            input("Press Enter to continue...")
    
    def view_doctor_info(self):
        """View doctor information"""
        clear_screen()
        
        doctor_id = input("\nEnter Doctor ID: ").strip()
        
        doctor = Doctor.load_doctor(doctor_id)
        
        if doctor:
            doctor.display()
            input("Press Enter to continue...")
        else:
            print(f"\n✗ Doctor {doctor_id} not found!")
            input("Press Enter to continue...")
    
    def view_doctor_slots(self):
        """View doctor's available slots"""
        clear_screen()
        
        doctor_id = input("\nEnter Doctor ID: ").strip()
        
        doctor = Doctor.load_doctor(doctor_id)
        
        if doctor:
            doctor.display_slots()
            input("Press Enter to continue...")
        else:
            print(f"\n✗ Doctor {doctor_id} not found!")
            input("Press Enter to continue...")
    
    def view_doctor_appointments(self):
        """View doctor's appointments"""
        clear_screen()
        
        doctor_id = input("\nEnter Doctor ID: ").strip()
        
        from utils import load_json_file
        from config import APPOINTMENT_DATA_FILE
        
        appointments = load_json_file(APPOINTMENT_DATA_FILE)
        doctor_apts = {
            apt_id: apt_data for apt_id, apt_data in appointments.items()
            if apt_data.get("doctor_id") == doctor_id
        }
        
        clear_screen()
        print("\n" + "="*70)
        print(f"{'APPOINTMENTS FOR: ' + doctor_id:^70}")
        print("="*70)
        
        if not doctor_apts:
            print("\nNo appointments found.")
        else:
            print(f"\n{'Appointment ID':<15} {'Patient ID':<15} {'Slot':<10} {'Time':<10} {'Status':<15}")
            print("-"*70)
            
            for apt_id, apt_data in doctor_apts.items():
                print(f"{apt_id:<15} {apt_data.get('patient_id', 'N/A'):<15} {apt_data.get('slot_id', 'N/A'):<10} {apt_data.get('appointment_time', 'N/A'):<10} {apt_data.get('status', 'N/A'):<15}")
        
        print("="*70 + "\n")
        input("Press Enter to continue...")
    
    def admin_panel(self):
        """
        Admin panel menu
        """
        while True:
            clear_screen()
            print_separator()
            print(f"\n{'ADMIN PANEL':^80}\n")
            print_separator()
            
            print("\nADMIN MENU\n")
            options = [
                "View System Status",
                "View All Patients",
                "View All Doctors",
                "View All Appointments",
                "Advance Time (Simulation)",
                "Reset System Time",
                "Back to Main Menu"
            ]
            
            for idx, option in enumerate(options, 1):
                print(f"{idx}. {option}")
            
            choice = input("\nSelect Option (1-7): ").strip()
            
            if choice == '1':
                self.admin_thread.display_status()
                input("Press Enter to continue...")
            elif choice == '2':
                self.view_all_patients()
            elif choice == '3':
                self.view_all_doctors()
            elif choice == '4':
                self.view_all_appointments()
            elif choice == '5':
                self.advance_time()
            elif choice == '6':
                TimeSimulation.reset_time()
                print("\n✓ System time reset!")
                input("Press Enter to continue...")
            elif choice == '7':
                break
            else:
                print("\n✗ Invalid choice! Press Enter to continue...")
                input()
    
    def view_all_patients(self):
        """View all patients"""
        clear_screen()
        
        from utils import load_json_file
        from config import PATIENT_DATA_FILE
        
        patients = load_json_file(PATIENT_DATA_FILE)
        
        print("\n" + "="*70)
        print(f"{'ALL PATIENTS':^70}")
        print("="*70)
        
        if not patients:
            print("\nNo patients found.")
        else:
            print(f"\n{'Patient ID':<15} {'Name':<20} {'Age':<8} {'Contact':<15}")
            print("-"*70)
            
            for pid, pdata in patients.items():
                print(f"{pid:<15} {pdata.get('name', 'N/A'):<20} {str(pdata.get('age', 'N/A')):<8} {pdata.get('contact', 'N/A'):<15}")
        
        print("="*70 + "\n")
        input("Press Enter to continue...")
    
    def view_all_doctors(self):
        """View all doctors"""
        clear_screen()
        
        from utils import load_json_file
        from config import DOCTOR_DATA_FILE
        
        doctors = load_json_file(DOCTOR_DATA_FILE)
        
        print("\n" + "="*70)
        print(f"{'ALL DOCTORS':^70}")
        print("="*70)
        
        if not doctors:
            print("\nNo doctors found.")
        else:
            print(f"\n{'Doctor ID':<15} {'Name':<20} {'Department':<20} {'Qualification':<15}")
            print("-"*70)
            
            for did, ddata in doctors.items():
                print(f"{did:<15} {ddata.get('name', 'N/A'):<20} {ddata.get('department', 'N/A'):<20} {ddata.get('qualification', 'N/A'):<15}")
        
        print("="*70 + "\n")
        input("Press Enter to continue...")
    
    def view_all_appointments(self):
        """View all appointments"""
        clear_screen()
        
        from utils import load_json_file
        from config import APPOINTMENT_DATA_FILE
        
        appointments = load_json_file(APPOINTMENT_DATA_FILE)
        
        print("\n" + "="*70)
        print(f"{'ALL APPOINTMENTS':^70}")
        print("="*70)
        
        if not appointments:
            print("\nNo appointments found.")
        else:
            print(f"\n{'Apt ID':<10} {'Patient':<10} {'Doctor':<10} {'Time':<10} {'Status':<15}")
            print("-"*70)
            
            for apt_id, apt_data in appointments.items():
                print(f"{apt_id:<10} {apt_data.get('patient_id', 'N/A'):<10} {apt_data.get('doctor_id', 'N/A'):<10} {apt_data.get('appointment_time', 'N/A'):<10} {apt_data.get('status', 'N/A'):<15}")
        
        print("="*70 + "\n")
        input("Press Enter to continue...")
    
    def advance_time(self):
        """Advance system time"""
        clear_screen()
        
        slots_input = input("\nEnter number of slots to advance (1-16): ").strip()
        
        try:
            slots = int(slots_input)
            if 1 <= slots <= 16:
                TimeSimulation.advance_time(slots)
                print(f"\n✓ Time advanced by {slots} slots")
                print(f"✓ Current time: {TimeSimulation.get_current_time()}")
            else:
                print("\n✗ Invalid number of slots!")
        except ValueError:
            print("\n✗ Please enter a valid number!")
        
        input("Press Enter to continue...")
    
    def view_system_status(self):
        """View overall system status"""
        clear_screen()
        
        from utils import load_json_file
        from config import PATIENT_DATA_FILE, DOCTOR_DATA_FILE, APPOINTMENT_DATA_FILE
        
        patients = load_json_file(PATIENT_DATA_FILE)
        doctors = load_json_file(DOCTOR_DATA_FILE)
        appointments = load_json_file(APPOINTMENT_DATA_FILE)
        
        print("\n" + "="*70)
        print(f"{'SYSTEM STATUS':^70}")
        print("="*70)
        print(f"\nTotal Patients      : {len(patients)}")
        print(f"Total Doctors       : {len(doctors)}")
        print(f"Total Appointments  : {len(appointments)}")
        
        confirmed = sum(1 for a in appointments.values() if a.get('status') == 'confirmed')
        print(f"Confirmed Apts      : {confirmed}")
        
        self.admin_thread.display_status()
        
        input("Press Enter to continue...")
    
    def exit_system(self):
        """Exit the system"""
        clear_screen()
        
        print("\n" + "="*70)
        print(f"{'THANK YOU FOR USING HOSPITAL MANAGEMENT SYSTEM':^70}")
        print("="*70)
        
        confirm = input("\nAre you sure you want to exit? (y/n): ").strip().lower()
        
        if confirm == 'y':
            print("\n✓ Exiting system...")
            self.admin_thread.stop()
            logger.info("System exited")
        else:
            pass
