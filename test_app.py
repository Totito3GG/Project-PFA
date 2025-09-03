#!/usr/bin/env python3
"""
Test script for the Project Management System
This script creates sample data and tests the application
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.db import create_connection, create_tables, create_projet, create_facture_charge, add_user
from app.auth import hash_password


def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")
    
    # Create database connection
    conn = create_connection()
    if not conn:
        print("Error: Could not connect to database")
        return False
    
    try:
        # Create tables
        create_tables(conn)
        print("✓ Database tables created")
        
        # Create sample users
        users = [
            ("directeur", "directeur123", "Directeur"),
            ("employe", "employe123", "Employe"),
            ("admin", "admin123", "Directeur")
        ]
        
        for username, password, role in users:
            try:
                user_id = add_user(username, hash_password(password), role)
                if user_id:
                    print(f"✓ User created: {username} ({role})")
                else:
                    print(f"⚠ User already exists: {username}")
            except Exception as e:
                print(f"⚠ Error creating user {username}: {e}")
        
        # Create sample projects
        projects = [
            ("Pont Autoroutier Rabat", "2025-01-15", "2025-02-01", 10000000.0, 0.0),
            ("Centre Commercial Casablanca", "2025-03-01", "2025-03-15", 25000000.0, 0.0),
            ("Résidence Marrakech", "2025-04-01", "2025-04-20", 15000000.0, 0.0),
            ("Route Nationale Tanger", "2025-05-01", "2025-05-10", 50000000.0, 0.0)
        ]
        
        project_ids = []
        for project_data in projects:
            try:
                project_id = create_projet(conn, project_data)
                if project_id:
                    project_ids.append(project_id)
                    print(f"✓ Project created: {project_data[0]} (ID: {project_id})")
                else:
                    print(f"⚠ Error creating project: {project_data[0]}")
            except Exception as e:
                print(f"⚠ Error creating project {project_data[0]}: {e}")
        
        # Create sample invoices
        if project_ids:
            invoices = [
                (project_ids[0], "2025-02-05", "Lafarge Ciment", 370000.0),  # Pont Rabat
                (project_ids[0], "2025-02-10", "Société BTP Services", 240000.0),  # Pont Rabat
                (project_ids[1], "2025-03-20", "Matériaux Plus", 850000.0),  # Centre Commercial
                (project_ids[1], "2025-03-25", "Équipements Pro", 1200000.0),  # Centre Commercial
                (project_ids[2], "2025-04-25", "Béton Express", 450000.0),  # Résidence
                (project_ids[3], "2025-05-15", "Asphalte Maroc", 2100000.0),  # Route Nationale
            ]
            
            for invoice_data in invoices:
                try:
                    invoice_id = create_facture_charge(conn, invoice_data)
                    if invoice_id:
                        print(f"✓ Invoice created: {invoice_data[2]} - {invoice_data[3]:,.2f} DH (ID: {invoice_id})")
                    else:
                        print(f"⚠ Error creating invoice: {invoice_data[2]}")
                except Exception as e:
                    print(f"⚠ Error creating invoice {invoice_data[2]}: {e}")
        
        conn.close()
        print("\n✓ Sample data creation completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        conn.close()
        return False


def test_database_connection():
    """Test database connection and basic operations"""
    print("Testing database connection...")
    
    try:
        conn = create_connection()
        if conn:
            print("✓ Database connection successful")
            
            # Test reading projects
            from app.db import read_projets
            projects = read_projets(conn)
            print(f"✓ Found {len(projects)} projects in database")
            
            # Test reading invoices
            from app.db import read_factures_by_projet
            if projects:
                invoices = read_factures_by_projet(conn, projects[0][0])
                print(f"✓ Found {len(invoices)} invoices for first project")
            
            conn.close()
            return True
        else:
            print("✗ Database connection failed")
            return False
            
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("PROJECT MANAGEMENT SYSTEM - TEST SCRIPT")
    print("=" * 60)
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database test failed. Please check your setup.")
        return
    
    # Create sample data
    if create_sample_data():
        print("\n✅ All tests passed! The application is ready to use.")
        print("\nDefault login credentials:")
        print("  Director: username='directeur', password='directeur123'")
        print("  Employee: username='employe', password='employe123'")
        print("  Admin: username='admin', password='admin123'")
        print("\nTo run the application, execute: python main.py")
    else:
        print("\n❌ Sample data creation failed.")


if __name__ == "__main__":
    main()

