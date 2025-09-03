from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QDateEdit, QDoubleSpinBox, QMessageBox, QGroupBox,
    QComboBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from app.db import create_connection, create_facture_charge, read_projets


class InvoiceFormDialog(QDialog):
    """Dialog for creating invoices"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_projects()
    
    def setup_ui(self):
        """Setup the form UI"""
        self.setWindowTitle("Nouvelle Facture")
        self.setModal(True)
        self.setFixedSize(500, 300)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Invoice info group
        info_group = QGroupBox("Informations de la Facture")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(10)
        
        # Project selection
        self.projet_combo = QComboBox()
        info_layout.addRow("Projet:", self.projet_combo)
        
        # Invoice date
        self.date_facture_edit = QDateEdit()
        self.date_facture_edit.setDate(QDate.currentDate())
        self.date_facture_edit.setCalendarPopup(True)
        self.date_facture_edit.setDisplayFormat("dd/MM/yyyy")
        info_layout.addRow("Date de la Facture:", self.date_facture_edit)
        
        # Supplier
        self.fournisseur_edit = QLineEdit()
        self.fournisseur_edit.setPlaceholderText("Nom du fournisseur")
        info_layout.addRow("Fournisseur:", self.fournisseur_edit)
        
        # Amount
        self.montant_spin = QDoubleSpinBox()
        self.montant_spin.setRange(0, 999999.99)
        self.montant_spin.setDecimals(2)
        self.montant_spin.setSuffix(" DH")
        self.montant_spin.setValue(0.0)
        info_layout.addRow("Montant Total:", self.montant_spin)
        
        main_layout.addWidget(info_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Save button
        self.save_btn = QPushButton("Créer")
        self.save_btn.clicked.connect(self.save_invoice)
        button_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(button_layout)
    
    def load_projects(self):
        """Load projects into combo box"""
        try:
            conn = create_connection()
            if conn:
                projects = read_projets(conn)
                for project in projects:
                    self.projet_combo.addItem(project[1], project[0])  # nom_projet, id_projet
                conn.close()
        except Exception as e:
            print(f"Error loading projects: {e}")
    
    def validate_form(self):
        """Validate form data"""
        if self.projet_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un projet")
            return False
        
        fournisseur = self.fournisseur_edit.text().strip()
        if not fournisseur:
            QMessageBox.warning(self, "Erreur", "Le nom du fournisseur est obligatoire")
            return False
        
        if self.montant_spin.value() <= 0:
            QMessageBox.warning(self, "Erreur", "Le montant doit être supérieur à 0")
            return False
        
        return True
    
    def save_invoice(self):
        """Save invoice data"""
        if not self.validate_form():
            return
        
        try:
            conn = create_connection()
            if not conn:
                QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données")
                return
            
            # Prepare invoice data
            project_id = self.projet_combo.currentData()
            date_facture = self.date_facture_edit.date().toString("yyyy-MM-dd")
            fournisseur = self.fournisseur_edit.text().strip()
            montant_total = self.montant_spin.value()
            
            # Create invoice
            invoice_tuple = (project_id, date_facture, fournisseur, montant_total)
            invoice_id = create_facture_charge(conn, invoice_tuple)
            
            if invoice_id:
                QMessageBox.information(self, "Succès", f"Facture créée avec succès (ID: {invoice_id})")
                self.accept()
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de créer la facture")
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")


def show_invoice_form(parent=None):
    """Show invoice form dialog"""
    dialog = InvoiceFormDialog(parent)
    return dialog.exec_() == dialog.Accepted
