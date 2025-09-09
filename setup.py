#!/usr/bin/env python3
"""
Setup Script for Project Management System
Initializes database and creates default users
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.db import create_connection, create_tables, add_user, get_user_by_username
from app.auth import hash_password


def setup_database():
    """Initialize database and create default users"""
    
    print("🔧 Setting up Project Management System...")
    print("=" * 50)
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        conn = create_connection()
        if not conn:
            raise Exception("Could not connect to database")
        
        create_tables(conn)
        conn.close()
        print("✅ Database tables created successfully")
        
        # Create default users if they don't exist
        print("👥 Creating default users...")
        
        # Default Director
        if not get_user_by_username("directeur"):
            add_user("directeur", hash_password("directeur123"), "Directeur")
            print("✅ Director user created (directeur/directeur123)")
        else:
            print("ℹ️  Director user already exists")
        
        # Default Employee
        if not get_user_by_username("employe"):
            add_user("employe", hash_password("employe123"), "Employe")
            print("✅ Employee user created (employe/employe123)")
        else:
            print("ℹ️  Employee user already exists")
        
        # Default Admin
        if not get_user_by_username("admin"):
            add_user("admin", hash_password("admin123"), "Directeur")
            print("✅ Admin user created (admin/admin123)")
        else:
            print("ℹ️  Admin user already exists")
        
        print("\n" + "=" * 50)
        print("🎉 Setup completed successfully!")
        print("🚀 You can now run the application with: python main.py")
        print("\n📝 Default Users:")
        print("   • Director: directeur/directeur123")
        print("   • Employee: employe/employe123")
        print("   • Admin: admin/admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
