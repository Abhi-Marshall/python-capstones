# Hospital Appointment Management System

A comprehensive Python-based hospital appointment management system with advanced threading, concurrency control, and persistent state management.

## 📋 Features

### 1. **Object-Oriented Design**
- **Patient Class**: Manages patient registration, information storage, and display
- **Doctor Class**: Handles doctor registration, slot management (10 AM - 6 PM, 30-min intervals)
- **Appointment Class**: Inherits from both Patient and Doctor, manages appointment linking and booking

### 2. **Threading & Concurrency**
- **Patient Thread**: Each patient login creates a dedicated thread
- **Doctor Thread**: Created when a patient books with a specific doctor
- **Booking Confirmation Thread**: Acquires locks for thread-safe slot booking
- **Admin Thread**: Controls global counter (timestamp simulation) and generates reports
- **Thread-Safe Operations**: Uses locks to prevent race conditions during simultaneous bookings

### 3. **Appointment Booking System**
- **Department Selection**: Patient chooses from 8 medical departments
- **Doctor Selection**: Lists available doctors in selected department
- **Slot Selection**: Displays doctor's available slots (10 AM - 6 PM, 30-min intervals)
- **Concurrent Booking**: Handles multiple patients trying to book same slot safely
- **Slot Lock Mechanism**: Prevents double-booking using threading locks

### 4. **Persistent State Management**
- **JSON-Based Storage**: All data stored in JSON files
- **Auto-Reload**: System resumes from previous state on restart
- **Data Files**:
  - `patient.json`: Patient registrations and information
  - `doctor.json`: Doctor registrations with available slots
  - `appointment.json`: All appointment bookings

### 5. **Comprehensive Logging**
- **Centralized Logging**: All actions logged to `logs/system.log`
- **Thread Information**: Each log entry includes thread name and ID
- **Detailed Tracking**: Patient login, registration, booking, errors, etc.
- **Log Format**: `[Timestamp] - [Level] - [ThreadName] - Message`

### 6. **Admin Panel & Time Simulation**
- **Global Counter**: Admin thread controls global timestamp
- **Diagnostic Reports**: Auto-generated when slots complete (30-min intervals)
- **System Status**: Monitor patients, doctors, appointments, current time
- **Report Generation**: Saves diagnostic reports to `reports/` directory
- **Modulo Reset**: Counter resets after 16 slots (full day simulation)

### 7. **Menu-Based Interface**
- **Hierarchical Menus**: Easy navigation with back options at every step
- **Patient Portal**: Register, login, book appointments, view history
- **Doctor Portal**: Register, manage slots, view appointments
- **Admin Panel**: System management and monitoring
- **Interactive Prompts**: Input validation and error handling

## 📁 Folder Structure

```
hospital/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration and constants
│   ├── utils.py               # Utility functions (logging, JSON, etc.)
│   ├── patient.py             # Patient class
│   ├── doctor.py              # Doctor class
│   ├── appointment.py         # Appointment class
│   ├── admin.py               # Admin thread handler
│   └── menu.py                # Menu interface
├── data/
│   ├── patient.json           # Persistent patient data
│   ├── doctor.json            # Persistent doctor data
│   └── appointment.json       # Persistent appointment data
├── logs/
│   └── system.log             # System activity logs
├── reports/
│   └── report_{patient_id}.json  # Diagnostic reports
├── main.py                    # Application entry point
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- macOS/Linux/Windows

### Installation Steps

1. **Navigate to the project directory**:
   ```bash
   cd /Users/as-mac-1233/Documents/hospital
   ```

2. **Install dependencies** (optional):
   ```bash
   pip install -r requirements.txt
   ```
   
   Note: The system uses only Python's standard library. The colorama package is optional for enhanced terminal output.

3. **Run the application**:
   ```bash
   python main.py
   ```

## 💻 Usage Guide

### Main Menu Options
1. **Patient Portal**
   - Register new patient
   - Login as existing patient
   - View patient information
   - Book appointment
   - View my appointments

2. **Doctor Portal**
   - Register new doctor
   - Login as existing doctor
   - View doctor information
   - View available slots
   - View appointments

3. **Admin Panel**
   - View system status
   - View all patients/doctors/appointments
   - Advance time simulation
   - Reset system time

### Appointment Booking Flow

1. **Register/Login as Patient**
   - Enter name, age, contact
   - System generates patient ID

2. **Book Appointment**
   - Select medical department
   - Choose doctor from available doctors
   - Select available time slot
   - Confirm booking

3. **Thread-Safe Booking**
   - If 2 patients try same slot: First one books, second gets "slot booked" message
   - Locks prevent race conditions
   - Atomic operations ensure data consistency

### Medical Departments
1. Cardiology
2. Neurology
3. Orthopedics
4. Dermatology
5. General Medicine
6. Pediatrics
7. Psychiatry
8. Urology

### Slot Timing
- **Start Time**: 10:00 AM
- **End Time**: 6:00 PM (18:00)
- **Interval**: 30 minutes
- **Total Slots**: 16 per day

## 🧵 Threading Architecture

### Thread Types

1. **Patient Thread** (`PatientThread-{patient_id}`)
   - Created when patient logs in
   - Handles patient actions
   - Manages booking requests

2. **Doctor Thread** (`DoctorThread-{doctor_id}`)
   - Created when appointment booking starts
   - Manages doctor availability
   - Processes slot allocation

3. **Booking Confirmation Thread**
   - Acquires per-slot locks
   - Prevents double-booking
   - Atomic slot reservation
   - Releases lock after confirmation

4. **Admin Thread** (`AdminThread`)
   - Singleton pattern (only one instance)
   - Controls global counter
   - Generates diagnostic reports
   - Runs continuously in background
   - Daemon thread (doesn't block exit)

### Thread Safety Mechanisms
- **Class-level locks**: `threading.Lock()` in Patient, Doctor, Appointment
- **Per-slot locks**: Dynamic lock creation for each slot
- **Atomic operations**: JSON file updates are atomic
- **Thread identification**: Each log entry includes thread info

## 📊 Data Models

### Patient Data Structure
```json
{
  "P0001": {
    "name": "John Doe",
    "age": 30,
    "contact": "9876543210",
    "thread_id": 12345,
    "thread_name": "PatientThread-P0001",
    "created_at": "2026-01-24T10:30:00",
    "status": "active"
  }
}
```

### Doctor Data Structure
```json
{
  "D0001": {
    "name": "Dr. Smith",
    "department": "Cardiology",
    "qualification": "MD",
    "thread_id": 12346,
    "thread_name": "DoctorThread-D0001",
    "created_at": "2026-01-24T09:00:00",
    "available_slots": [
      {
        "slot_id": 0,
        "time": "10:00",
        "booked": false,
        "booked_by": null,
        "booked_at": null
      }
    ],
    "status": "active"
  }
}
```

### Appointment Data Structure
```json
{
  "A0001": {
    "patient_id": "P0001",
    "doctor_id": "D0001",
    "slot_id": 3,
    "appointment_time": "11:30",
    "status": "confirmed",
    "created_at": "2026-01-24T10:35:00",
    "confirmed_at": "2026-01-24T10:35:15",
    "thread_id": 12345,
    "thread_name": "PatientThread-P0001"
  }
}
```

### Diagnostic Report Structure
```json
[
  {
    "appointment_id": "A0001",
    "patient_id": "P0001",
    "doctor_id": "D0001",
    "slot_id": 3,
    "timestamp": "2026-01-24T11:30:00",
    "consultation_notes": "Consultation completed at slot 3",
    "vitals": {
      "blood_pressure": "120/80",
      "heart_rate": "72 bpm",
      "temperature": "98.6°F"
    },
    "diagnosis": "Routine checkup completed",
    "prescription": "Take rest and maintain healthy diet",
    "follow_up": "After 3 months"
  }
]
```

## 📝 Logging Details

### Log File Location
- **Path**: `logs/system.log`
- **Format**: `[YYYY-MM-DD HH:MM:SS] - [LEVEL] - [ThreadName] - Message`

### Log Levels
- **INFO**: Normal operations (registrations, bookings, data loads)
- **WARNING**: Potential issues (invalid input, not found)
- **ERROR**: Failures (database errors, booking failures)
- **DEBUG**: Detailed information (function calls, variable states)

### Example Log Entries
```
[2026-01-24 10:30:15] - [INFO] - MainThread - Hospital Appointment Management System - STARTED
[2026-01-24 10:30:16] - [INFO] - MainThread - Admin Thread initialized
[2026-01-24 10:31:00] - [INFO] - PatientThread-P0001 - New patient created: P0001 - John Doe
[2026-01-24 10:32:45] - [INFO] - PatientThread-P0001 - Patient P0001 selected department: Cardiology
[2026-01-24 10:33:20] - [INFO] - PatientThread-P0001 - Patient P0001 selected slot 3 for doctor D0001
[2026-01-24 10:33:25] - [INFO] - BookingConfirmationThread - Booking confirmation thread acquired lock for slot D0001_3
[2026-01-24 10:33:26] - [INFO] - BookingConfirmationThread - Appointment A0001 confirmed for patient P0001
```

## 🔒 Race Condition Handling

### Scenario: Two Patients Booking Same Slot

**Before Lock**:
```
Thread 1 (Patient A): Checks slot 3 → Available
Thread 2 (Patient B): Checks slot 3 → Available
Thread 1: Books slot 3
Thread 2: Books same slot 3 (ERROR - Double booking!)
```

**With Lock Mechanism**:
```
Thread 1 (Patient A): Acquires lock for slot D0001_3
Thread 2 (Patient B): Waits for lock...
Thread 1: Checks slot 3 → Available
Thread 1: Books slot 3
Thread 1: Releases lock
Thread 2: Acquires lock
Thread 2: Checks slot 3 → Already booked!
Thread 2: Shows "Slot is no longer available"
```

## 📊 Admin Thread & Time Simulation

### Counter Management
- **Starting Value**: 0
- **Increments**: By 1 for each slot completion (30 minutes)
- **Reset Value**: Modulo 16 (resets after full day)
- **Conversion**: Counter → Time (Counter × 30 min + 10:00 AM)

### Example Timeline
```
Counter 0 → 10:00 AM
Counter 1 → 10:30 AM
Counter 2 → 11:00 AM
Counter 3 → 11:30 AM
...
Counter 15 → 5:30 PM
Counter 0 → 10:00 AM (Reset)
```

### Diagnostic Report Generation
- Generated when counter completes a slot
- Matches appointments to current slot
- Includes vitals, diagnosis, prescription
- Saved to `reports/report_{patient_id}.json`

## 🛡️ Error Handling

### Patient Registration Errors
- Empty name: Prompt to re-enter
- Invalid age: Validate numeric and positive
- Invalid contact: Validate length (minimum 10 digits)

### Appointment Booking Errors
- Slot already booked: Display message and suggest other slots
- Invalid department: Show available departments
- No doctors in department: Notify and suggest alternatives
- Doctor not found: Database error handling

### File I/O Errors
- JSON decode errors: Return empty dict, log warning
- File not found: Create default structure
- Write failures: Log error, notify user

## 🧪 Testing the System

### Test Scenario 1: Basic Patient Registration
1. Start application
2. Choose "Patient Portal" → "Register New Patient"
3. Enter details (name, age, contact)
4. Verify patient ID generated
5. Check `data/patient.json` for entry

### Test Scenario 2: Single Appointment Booking
1. Register patient
2. Register doctor in any department
3. Login as patient
4. "Book Appointment" → Select department → Select doctor → Select slot
5. Confirm booking
6. Verify in `data/appointment.json`

### Test Scenario 3: Concurrent Booking (Race Condition)
1. Register 2 patients
2. Register 1 doctor
3. In parallel terminals: Both try to book same slot
4. Observe: One books, other gets "slot booked" message
5. Check logs for lock acquisition

### Test Scenario 4: State Persistence
1. Register patients and doctors
2. Book appointments
3. Exit application
4. Restart application
5. Verify all data is restored from JSON files

### Test Scenario 5: Time Simulation
1. Open Admin Panel
2. "Advance Time (Simulation)" → Enter slots (e.g., 3)
3. Check current time updates
4. Monitor `reports/` for diagnostic reports

## 📚 Key Concepts Implemented

### 1. **Object-Oriented Programming (OOP)**
- Inheritance: Appointment inherits from Patient and Doctor
- Encapsulation: Private methods and class-level attributes
- Polymorphism: Overridden display() methods
- Abstraction: Complex threading abstracted in AdminThread

### 2. **Concurrency**
- Thread creation and management
- Lock mechanisms for race condition prevention
- Daemon threads for background tasks
- Singleton pattern for Admin thread

### 3. **File I/O & Persistence**
- JSON serialization/deserialization
- Atomic file operations
- State recovery on restart
- ETL pattern for data transformation

### 4. **Logging & Monitoring**
- Centralized logging system
- Thread-aware logging
- Log levels and formatting
- Activity tracking

### 5. **Design Patterns**
- Singleton: AdminThread (single instance)
- Factory: Patient/Doctor/Appointment creation methods
- Thread Pool: Multiple concurrent threads
- Lock Pattern: Atomic operations

## 🐛 Troubleshooting

### Issue: "No module named 'src'"
**Solution**: Run from project root directory with `python main.py`

### Issue: "Permission denied" on logs/
**Solution**: Check folder permissions, run with appropriate access

### Issue: JSON decode error
**Solution**: Delete corrupted JSON files, they'll be recreated on next run

### Issue: Slot already booked immediately
**Solution**: Check another patient thread; implement thread delays in testing

### Issue: Admin thread not generating reports
**Solution**: Ensure time simulation is advancing (use Admin Panel → Advance Time)

## 📞 Support

For issues or questions, check:
1. `logs/system.log` for error details
2. `data/` folder for state information
3. Thread names in logs for concurrent operation tracking

## 📄 License

Educational project - Hospital Management System

## 👨‍💻 Technical Stack

- **Language**: Python 3.8+
- **Concurrency**: threading module
- **Data Storage**: JSON files
- **Logging**: Python logging module
- **Architecture**: Multi-threaded OOP
- **Design Pattern**: Singleton, Factory, Observer

---

**Last Updated**: 24 January 2026
**Version**: 1.0.0
