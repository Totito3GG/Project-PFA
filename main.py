#!/usr/bin/env python3
"""
Système de Gestion de Projets & Charges
Main application entry point
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.db import create_connection, create_tables, add_user
from app.auth import hash_password
from app.gui.login import SignInDialog
from app.gui.main_window import MainApplicationWindow


class ProjectManagementApp:
    """Main application class"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Système de Gestion de Projets & Charges")
        self.app.setApplicationVersion("1.0.0")
        
        # Set application style
        self.app.setStyle('Fusion')
        
        # Initialize database
        self.init_database()
        
        # Create default users if they don't exist
        self.create_default_users()
        
        # Show splash screen
        self.show_splash_screen()
        
        # Show login dialog
        self.show_login()
    
    def init_database(self):
        """Initialize database and create tables"""
        try:
            conn = create_connection()
            if conn:
                create_tables(conn)
                conn.close()
                print("Database initialized successfully")
            else:
                raise Exception("Could not connect to database")
        except Exception as e:
            QMessageBox.critical(None, "Erreur de Base de Données", 
                               f"Impossible d'initialiser la base de données:\n{str(e)}")
            sys.exit(1)
    
    def create_default_users(self):
        """Create default users if they don't exist"""
        try:
            from app.db import get_user_by_username
            
            # Create default director
            if not get_user_by_username("directeur"):
                add_user("directeur", hash_password("directeur123"), "Directeur")
                print("Default director user created")
            
            # Create default employee
            if not get_user_by_username("employe"):
                add_user("employe", hash_password("employe123"), "Employe")
                print("Default employee user created")
                
        except Exception as e:
            print(f"Warning: Could not create default users: {e}")
    
    def show_splash_screen(self):
        """Show splash screen during application startup"""
        # Create a simple splash screen
        splash_pix = QPixmap(400, 300)
        splash_pix.fill(Qt.blue)
        
        self.splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        self.splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Add text to splash screen
        self.splash.showMessage("Initialisation du système...", 
                              Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        self.splash.show()
        
        # Process events to show splash screen
        self.app.processEvents()
        
        # Hide splash screen after a delay
        QTimer.singleShot(2000, self.splash.close)
    
    def show_login(self):
        """Show login dialog"""
        login_dialog = SignInDialog()
        
        if login_dialog.exec_() == login_dialog.Accepted:
            # Login successful, get user data and show main window
            user_data = getattr(login_dialog, 'user_data', None)
            self.show_main_window(user_data)
        else:
            # Login cancelled or failed
            sys.exit(0)
    
    def show_main_window(self, user_data=None):
        """Show main application window"""
        try:
            self.main_window = MainApplicationWindow(user_data)
            self.main_window.show()
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print full traceback
            QMessageBox.critical(None, "Error", 
                               f"Unable to open main window:\n{str(e)}")
            sys.exit(1)
    
    def run(self):
        """Run the application"""
        return self.app.exec_()


def main():
    """Main function"""
    try:
        # Create and run application
        app = ProjectManagementApp()
        sys.exit(app.run())
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()