"""
Main Application Entry Point
Hospital Appointment Management System
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import threading
from src.menu import MenuInterface
from src.admin import AdminThread
from src.utils import get_logger

logger = get_logger(__name__)


def main():
    """
    Main entry point for the application
    """
    try:
        logger.info("="*70)
        logger.info("Hospital Appointment Management System - STARTED")
        logger.info("="*70)
        
        # Initialize admin thread
        admin_thread = AdminThread.get_instance()
        admin_thread.start()
        
        logger.info("Admin thread started")
        
        # Initialize menu interface
        menu = MenuInterface()
        
        # Start main menu
        menu.main_menu()
        
        logger.info("="*70)
        logger.info("Hospital Appointment Management System - STOPPED")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        print(f"\n✗ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
