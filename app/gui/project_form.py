from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QDateEdit, QDoubleSpinBox, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from app.db import create_connection, create_projet, update_projet, read_projets
from app.models import Project
from app.utils import validate_budget, get_current_date_str


class ProjectFormDialog(QDialog):
    """Dialog for creating and editing projects"""
    
    def __init__(self, project_data=None, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.is_edit_mode = project_data is not None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the form UI"""
        title = "Modifier Projet" if self.is_edit_mode else "Nouveau Projet"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Form group
        form_group = QGroupBox("Informations du Projet")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(15)
        
        # Project name
        self.nom_projet_edit = QLineEdit()
        self.nom_projet_edit.setPlaceholderText("Nom du projet")
        self.nom_projet_edit.setFont(QFont("Arial", 10))
        form_layout.addRow("Nom du Projet:", self.nom_projet_edit)
        
        # Estimation date
        self.date_estimation_edit = QDateEdit()
        self.date_estimation_edit.setDate(QDate.currentDate())
        self.date_estimation_edit.setCalendarPopup(True)
        self.date_estimation_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Date d'Estimation:", self.date_estimation_edit)
        
        # Launch date
        self.date_lancement_edit = QDateEdit()
        self.date_lancement_edit.setDate(QDate.currentDate())
        self.date_lancement_edit.setCalendarPopup(True)
        self.date_lancement_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Date de Lancement:", self.date_lancement_edit)
        
        # Budget max
        self.budget_max_spin = QDoubleSpinBox()
        self.budget_max_spin.setRange(0, 999999999.99)
        self.budget_max_spin.setDecimals(2)
        self.budget_max_spin.setSuffix(" DH")
        self.budget_max_spin.setValue(0.0)
        form_layout.addRow("Budget Maximum:", self.budget_max_spin)
        
        # Amount invested (read-only for edit mode)
        self.montant_investi_spin = QDoubleSpinBox()
        self.montant_investi_spin.setRange(0, 999999999.99)
        self.montant_investi_spin.setDecimals(2)
        self.montant_investi_spin.setSuffix(" DH")
        self.montant_investi_spin.setValue(0.0)
        if self.is_edit_mode:
            self.montant_investi_spin.setReadOnly(True)
            self.montant_investi_spin.setStyleSheet("background-color: #f0f0f0;")
        form_layout.addRow("Montant Investi:", self.montant_investi_spin)
        
        main_layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Save button
        save_text = "Modifier" if self.is_edit_mode else "Créer"
        self.save_btn = QPushButton(save_text)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.save_btn.clicked.connect(self.save_project)
        button_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(button_layout)
    
    def load_data(self):
        """Load project data into form fields"""
        if self.project_data:
            self.nom_projet_edit.setText(self.project_data.get('nom_projet', ''))
            
            # Load dates
            date_estimation = self.project_data.get('date_estimation', '')
            if date_estimation:
                try:
                    from datetime import datetime
                    dt = datetime.strptime(date_estimation, '%Y-%m-%d')
                    self.date_estimation_edit.setDate(QDate(dt.year, dt.month, dt.day))
                except:
                    pass
            
            date_lancement = self.project_data.get('date_lancement', '')
            if date_lancement:
                try:
                    from datetime import datetime
                    dt = datetime.strptime(date_lancement, '%Y-%m-%d')
                    self.date_lancement_edit.setDate(QDate(dt.year, dt.month, dt.day))
                except:
                    pass
            
            # Load amounts
            self.budget_max_spin.setValue(self.project_data.get('budget_max', 0.0))
            self.montant_investi_spin.setValue(self.project_data.get('montant_investi', 0.0))
    
    def validate_form(self):
        """Validate form data"""
        # Check project name
        nom_projet = self.nom_projet_edit.text().strip()
        if not nom_projet:
            QMessageBox.warning(self, "Erreur", "Le nom du projet est obligatoire")
            self.nom_projet_edit.setFocus()
            return False
        
        # Check budget
        budget_max = self.budget_max_spin.value()
        if budget_max <= 0:
            QMessageBox.warning(self, "Erreur", "Le budget maximum doit être supérieur à 0")
            self.budget_max_spin.setFocus()
            return False
        
        # Check dates
        date_estimation = self.date_estimation_edit.date()
        date_lancement = self.date_lancement_edit.date()
        
        if date_lancement < date_estimation:
            QMessageBox.warning(self, "Erreur", "La date de lancement ne peut pas être antérieure à la date d'estimation")
            self.date_lancement_edit.setFocus()
            return False
        
        return True
    
    def save_project(self):
        """Save project data"""
        if not self.validate_form():
            return
        
        try:
            conn = create_connection()
            if not conn:
                QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données")
                return
            
            # Prepare data
            nom_projet = self.nom_projet_edit.text().strip()
            date_estimation = self.date_estimation_edit.date().toString("yyyy-MM-dd")
            date_lancement = self.date_lancement_edit.date().toString("yyyy-MM-dd")
            budget_max = self.budget_max_spin.value()
            montant_investi = self.montant_investi_spin.value()
            
            if self.is_edit_mode:
                # Update existing project
                project_tuple = (nom_projet, date_estimation, date_lancement, budget_max, montant_investi, self.project_data['id_projet'])
                success = update_projet(conn, project_tuple)
                
                if success:
                    QMessageBox.information(self, "Succès", "Projet modifié avec succès")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Erreur", "Impossible de modifier le projet")
            else:
                # Create new project
                project_tuple = (nom_projet, date_estimation, date_lancement, budget_max, montant_investi)
                project_id = create_projet(conn, project_tuple)
                
                if project_id:
                    QMessageBox.information(self, "Succès", f"Projet créé avec succès (ID: {project_id})")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Erreur", "Impossible de créer le projet")
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")


def show_project_form(project_data=None, parent=None):
    """Show project form dialog"""
    dialog = ProjectFormDialog(project_data, parent)
    return dialog.exec_() == dialog.Accepted