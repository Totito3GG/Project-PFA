#!/usr/bin/env python3
"""
Debug Login Issue
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.gui.login import SignInDialog


def test_login():
    """Test login dialog"""
    app = QApplication(sys.argv)
    
    try:
        dialog = SignInDialog()
        print("✅ SignInDialog created successfully")
        print("Now test clicking 'Forgot Password' or 'Create New Account'")
        print("The dialog should stay open and return to the login screen")
        
        # Show dialog
        result = dialog.exec_()
        print(f"Dialog result: {result}")
        
        if result == 1:  # QDialog.Accepted = 1
            print("✅ User signed in successfully")
            user_data = getattr(dialog, 'user_data', None)
            print(f"User data: {user_data}")
        else:
            print("❌ Login cancelled or failed")
    
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        traceback.print_exc()
    
    sys.exit(0)


if __name__ == "__main__":
    test_login()
