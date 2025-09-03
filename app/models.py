from datetime import datetime
from typing import List, Optional


class Project:
    """Project model with business logic"""
    
    def __init__(self, id_projet=None, nom_projet="", date_estimation=None, 
                 date_lancement=None, budget_max=0.0, montant_investi=0.0):
        self.id_projet = id_projet
        self.nom_projet = nom_projet
        self.date_estimation = date_estimation
        self.date_lancement = date_lancement
        self.budget_max = float(budget_max)
        self.montant_investi = float(montant_investi)
    
    @property
    def reste_budget(self):
        """Calculate remaining budget"""
        return self.budget_max - self.montant_investi
    
    @property
    def pourcentage_utilise(self):
        """Calculate percentage of budget used"""
        if self.budget_max == 0:
            return 0
        return (self.montant_investi / self.budget_max) * 100
    
    @property
    def is_over_budget(self):
        """Check if project is over budget"""
        return self.montant_investi > self.budget_max
    
    def to_tuple(self):
        """Convert to tuple for database operations"""
        return (self.nom_projet, self.date_estimation, self.date_lancement, 
                self.budget_max, self.montant_investi)
    
    def to_tuple_with_id(self):
        """Convert to tuple with ID for updates"""
        return (self.nom_projet, self.date_estimation, self.date_lancement, 
                self.budget_max, self.montant_investi, self.id_projet)
    
    @classmethod
    def from_tuple(cls, data):
        """Create Project from database tuple"""
        if len(data) >= 6:
            return cls(data[0], data[1], data[2], data[3], data[4], data[5])
        return None
    
    def __str__(self):
        return f"Project: {self.nom_projet} (Budget: {self.budget_max:,.2f} DH)"


class Invoice:
    """Invoice model for project charges"""
    
    def __init__(self, id_facture_charge=None, id_projet=None, date_facture=None, 
                 fournisseur="", montant_total=0.0):
        self.id_facture_charge = id_facture_charge
        self.id_projet = id_projet
        self.date_facture = date_facture
        self.fournisseur = fournisseur
        self.montant_total = float(montant_total)
        self.lignes = []  # List of Line objects
    
    def add_line(self, line):
        """Add a line to this invoice"""
        if isinstance(line, Line):
            line.id_facture_charge = self.id_facture_charge
            self.lignes.append(line)
            self.recalculate_total()
    
    def recalculate_total(self):
        """Recalculate total from lines"""
        self.montant_total = sum(line.montant_total for line in self.lignes)
    
    def to_tuple(self):
        """Convert to tuple for database operations"""
        return (self.id_projet, self.date_facture, self.fournisseur, self.montant_total)
    
    @classmethod
    def from_tuple(cls, data):
        """Create Invoice from database tuple"""
        if len(data) >= 5:
            return cls(data[0], data[1], data[2], data[3], data[4])
        return None
    
    def __str__(self):
        return f"Invoice: {self.fournisseur} - {self.montant_total:,.2f} DH"


class Line:
    """Line item model for invoice details"""
    
    def __init__(self, id_ligne=None, id_facture_charge=None, motif="", 
                 prix_unitaire=0.0, quantite=0.0, montant_total=0.0):
        self.id_ligne = id_ligne
        self.id_facture_charge = id_facture_charge
        self.motif = motif
        self.prix_unitaire = float(prix_unitaire)
        self.quantite = float(quantite)
        self.montant_total = float(montant_total)
    
    def calculate_total(self):
        """Calculate total amount"""
        self.montant_total = self.prix_unitaire * self.quantite
        return self.montant_total
    
    def to_tuple(self):
        """Convert to tuple for database operations"""
        return (self.id_facture_charge, self.motif, self.prix_unitaire, 
                self.quantite, self.montant_total)
    
    @classmethod
    def from_tuple(cls, data):
        """Create Line from database tuple"""
        if len(data) >= 6:
            return cls(data[0], data[1], data[2], data[3], data[4], data[5])
        return None
    
    def __str__(self):
        return f"Line: {self.motif} - {self.quantite} x {self.prix_unitaire:,.2f} = {self.montant_total:,.2f} DH"


class User:
    """User model for authentication and authorization"""
    
    def __init__(self, id_user=None, username="", password="", role=""):
        self.id_user = id_user
        self.username = username
        self.password = password
        self.role = role
    
    @property
    def is_director(self):
        """Check if user is a director"""
        return self.role == 'Directeur'
    
    @property
    def is_employee(self):
        """Check if user is an employee"""
        return self.role == 'Employe'
    
    @property
    def can_edit(self):
        """Check if user can edit data (only directors)"""
        return self.is_director
    
    @property
    def can_view_only(self):
        """Check if user can only view data (employees)"""
        return self.is_employee
    
    def to_tuple(self):
        """Convert to tuple for database operations"""
        return (self.username, self.password, self.role)
    
    @classmethod
    def from_tuple(cls, data):
        """Create User from database tuple"""
        if len(data) >= 4:
            return cls(data[0], data[1], data[2], data[3])
        return None
    
    def __str__(self):
        return f"User: {self.username} ({self.role})"


class ProjectReport:
    """Report model for project financial summary"""
    
    def __init__(self, project: Project, invoices: List[Invoice] = None):
        self.project = project
        self.invoices = invoices or []
        self.total_charges = sum(inv.montant_total for inv in self.invoices)
        self.reste_budget = project.budget_max - self.total_charges
        self.pourcentage_utilise = (self.total_charges / project.budget_max * 100) if project.budget_max > 0 else 0
    
    def get_summary(self):
        """Get project summary as dictionary"""
        return {
            'nom_projet': self.project.nom_projet,
            'budget_max': self.project.budget_max,
            'total_charges': self.total_charges,
            'reste_budget': self.reste_budget,
            'pourcentage_utilise': self.pourcentage_utilise,
            'nombre_factures': len(self.invoices),
            'is_over_budget': self.reste_budget < 0
        }