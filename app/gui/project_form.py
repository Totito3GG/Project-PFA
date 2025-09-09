from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QDateEdit, QDoubleSpinBox, QMessageBox, QGroupBox, QFrame
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
        """Setup the form UI to match modern dashboard design"""
        title = "Modifier Projet" if self.is_edit_mode else "Nouveau Projet"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(520, 480)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QLabel(title)
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setStyleSheet("color: #2d3748; padding: 16px 16px 0 16px;")
        main_layout.addWidget(header)

        # Form card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #fff;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
                margin: 12px 16px 0 16px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(18)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(18)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Project name
        self.nom_projet_edit = QLineEdit()
        self.nom_projet_edit.setPlaceholderText("Nom du projet")
        self.nom_projet_edit.setFont(QFont("Arial", 12))
        self.nom_projet_edit.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 15px;
                background: #f9fafb;
            }
            QLineEdit:focus {
                border-color: #ed8936;
                background: #fff;
            }
        """)
        form_layout.addRow("<b>Nom du Projet</b>", self.nom_projet_edit)

        # Estimation date
        self.date_estimation_edit = QDateEdit()
        self.date_estimation_edit.setDate(QDate.currentDate())
        self.date_estimation_edit.setCalendarPopup(True)
        self.date_estimation_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_estimation_edit.setStyleSheet("""
            QDateEdit {
                border: 1.5px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 15px;
                background: #f9fafb;
            }
            QDateEdit:focus {
                border-color: #ed8936;
                background: #fff;
            }
        """)
        form_layout.addRow("<b>Date de fin du projet</b>", self.date_estimation_edit)

        # Launch date
        self.date_lancement_edit = QDateEdit()
        self.date_lancement_edit.setDate(QDate.currentDate())
        self.date_lancement_edit.setCalendarPopup(True)
        self.date_lancement_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_lancement_edit.setStyleSheet("""
            QDateEdit {
                border: 1.5px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 15px;
                background: #f9fafb;
            }
            QDateEdit:focus {
                border-color: #ed8936;
                background: #fff;
            }
        """)
        form_layout.addRow("<b>Date de Lancement</b>", self.date_lancement_edit)

        # Budget max
        self.budget_max_spin = QDoubleSpinBox()
        self.budget_max_spin.setRange(0, 999999999.99)
        self.budget_max_spin.setDecimals(2)
        self.budget_max_spin.setSuffix(" DH")
        self.budget_max_spin.setValue(0.0)
        self.budget_max_spin.setFont(QFont("Arial", 12))
        self.budget_max_spin.setStyleSheet("""
            QDoubleSpinBox {
                border: 1.5px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 15px;
                background: #f9fafb;
            }
            QDoubleSpinBox:focus {
                border-color: #ed8936;
                background: #fff;
            }
        """)
        form_layout.addRow("<b>Budget Maximum</b>", self.budget_max_spin)

        # Amount invested (read-only for edit mode)
        self.montant_investi_spin = QDoubleSpinBox()
        self.montant_investi_spin.setRange(0, 999999999.99)
        self.montant_investi_spin.setDecimals(2)
        self.montant_investi_spin.setSuffix(" DH")
        self.montant_investi_spin.setValue(0.0)
        self.montant_investi_spin.setFont(QFont("Arial", 12))
        if self.is_edit_mode:
            self.montant_investi_spin.setReadOnly(True)
            self.montant_investi_spin.setStyleSheet("background-color: #f0f0f0; border-radius: 8px;")
        else:
            self.montant_investi_spin.setStyleSheet("""
                QDoubleSpinBox {
                    border: 1.5px solid #cbd5e1;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 15px;
                    background: #f9fafb;
                }
                QDoubleSpinBox:focus {
                    border-color: #ed8936;
                    background: #fff;
                }
            """)
        form_layout.addRow("<b>Montant Investi</b>", self.montant_investi_spin)

        card_layout.addLayout(form_layout)
        main_layout.addWidget(card)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(16, 16, 16, 16)
        button_layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e2e8f0;
                color: #2d3748;
                border: none;
                padding: 10px 28px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #cbd5e1;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # Save button
        save_text = "Modifier" if self.is_edit_mode else "Créer"
        self.save_btn = QPushButton(save_text)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #ed8936;
                color: white;
                border: none;
                padding: 10px 28px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #dd6b20;
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
        
        if date_estimation < date_lancement:
            QMessageBox.warning(self, "Erreur", "La date de fin du projet ne peut pas être antérieure à la date de lancement")
            self.date_estimation_edit.setFocus()
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