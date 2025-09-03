from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QStatusBar, QFrame,
    QStackedWidget, QListWidget, QListWidgetItem, QPushButton, QLabel
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QColor
from datetime import datetime

from app.db import create_connection, read_projets
from app.utils import format_currency, format_date
from app.gui.project_form import show_project_form
from app.gui.invoice_form import show_invoice_form


class MainApplicationWindow(QMainWindow):
    """Main application window with modern dashboard design"""
    
    def __init__(self):
        super().__init__()
        self.current_page = "projects"

        try:
            self.setup_ui()
            self.load_data()
            
            # Auto-refresh data every 30 seconds
            self.refresh_timer = QTimer()
            self.refresh_timer.timeout.connect(self.load_data)
            self.refresh_timer.start(30000)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
    
    def setup_ui(self):
        """Setup the main window UI with modern dashboard design"""
        self.setWindowTitle("Project Management Dashboard")
        self.setGeometry(100, 100, 1280, 720)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.create_sidebar(main_layout)

        # Main content
        self.create_main_content(main_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def create_sidebar(self, parent_layout):
        """Create the sidebar navigation"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #1a202c;
                border: none;
            }
        """)

        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo area
        logo_frame = QFrame()
        logo_frame.setFixedHeight(100)
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        pixmap = QPixmap(r"C:\Users\mosta\OneDrive\Bureau\Project\v0.1\Images\logo.jpg")
        pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)

        layout.addWidget(logo_frame)

        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: #1a202c;
                border: none;
                color: #e2e8f0;
                font-size: 14px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                margin: 4px 8px;
            }
            QListWidget::item:selected {
                background-color: #ed8936;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #2d3748;
            }
        """)
        nav_items = [
            ("📊", "Projects"),
            ("📄", "Invoices"),
            ("💰", "Expenses"),
            ("📈", "Reports"),
            ("👥", "Users")
        ]
        for icon, text in nav_items:
            item = QListWidgetItem(f"{icon}  {text}")
            item.setData(Qt.UserRole, text.lower())
            self.nav_list.addItem(item)
        self.nav_list.setCurrentRow(0)
        self.nav_list.currentItemChanged.connect(self.on_navigation_changed)

        layout.addWidget(self.nav_list)
        layout.addStretch()

        parent_layout.addWidget(self.sidebar)

    def create_main_content(self, parent_layout):
        """Create the main content area"""
        self.main_content = QFrame()
        self.main_content.setStyleSheet("""
            QFrame {
                background-color: #f7fafc;
                border: none;
            }
        """)

        layout = QVBoxLayout(self.main_content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Stacked pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Create pages
        self.create_projects_page()
        self.create_invoices_page()
        self.create_expenses_page()
        self.create_reports_page()
        self.create_users_page()

        self.stacked_widget.setCurrentWidget(self.projects_page)
        parent_layout.addWidget(self.main_content)

    def create_projects_page(self):
        """Create projects page with table design"""
        self.projects_page = QWidget()
        layout = QVBoxLayout(self.projects_page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        welcome_label = QLabel("Welcome, Director")
        welcome_label.setFont(QFont("Arial", 16))
        welcome_label.setStyleSheet("color: #2d3748;")
        header_layout.addWidget(welcome_label)
        
        header_layout.addStretch()
        
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ed8936;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dd6b20;
            }
        """)
        header_layout.addWidget(logout_btn)
        layout.addLayout(header_layout)
        
        # Title + Add button
        title_layout = QHBoxLayout()
        title_label = QLabel("Active Projects")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2d3748;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        self.add_project_btn = QPushButton("Add Project")
        self.add_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #ed8936;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #dd6b20;
            }
        """)
        self.add_project_btn.clicked.connect(self.create_new_project)
        title_layout.addWidget(self.add_project_btn)
        layout.addLayout(title_layout)

        # Projects table
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(4)
        self.projects_table.setHorizontalHeaderLabels([
            "Project Name", "Budget", "Remaining", "Status"
        ])
        self.projects_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #e2e8f0;
                selection-background-color: #edf2f7;
            }
            QHeaderView::section {
                background-color: #f7fafc;
                padding: 15px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #2d3748;
            }
        """)
        header = self.projects_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.projects_table.setAlternatingRowColors(True)
        self.projects_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.projects_table.setShowGrid(False)
        
        # Connect double-click to view project details
        self.projects_table.cellDoubleClicked.connect(self.on_project_double_clicked)
        
        layout.addWidget(self.projects_table)

        self.stacked_widget.addWidget(self.projects_page)

    def create_invoices_page(self):
        self.invoices_page = QWidget()
        layout = QVBoxLayout(self.invoices_page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header with title and buttons
        header_layout = QHBoxLayout()
        title_label = QLabel("Invoices")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2d3748;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Action buttons
        self.new_invoice_btn = QPushButton("New Invoice")
        self.new_invoice_btn.setStyleSheet("""
            QPushButton {
                background-color: #ed8936;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #dd6b20;
            }
        """)
        self.new_invoice_btn.clicked.connect(self.create_new_invoice)
        header_layout.addWidget(self.new_invoice_btn)

        self.edit_invoice_btn = QPushButton("Edit")
        self.edit_invoice_btn.setStyleSheet("""
            QPushButton {
                background-color: #3182ce;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2c5aa0;
            }
        """)
        self.edit_invoice_btn.clicked.connect(self.edit_invoice)
        self.edit_invoice_btn.setEnabled(False)
        header_layout.addWidget(self.edit_invoice_btn)

        self.delete_invoice_btn = QPushButton("Delete")
        self.delete_invoice_btn.setStyleSheet("""
            QPushButton {
                background-color: #e53e3e;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c53030;
            }
        """)
        self.delete_invoice_btn.clicked.connect(self.delete_invoice)
        self.delete_invoice_btn.setEnabled(False)
        header_layout.addWidget(self.delete_invoice_btn)
        
        layout.addLayout(header_layout)
        
        # Invoices table
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(5)
        self.invoices_table.setHorizontalHeaderLabels([
            "#", "Date", "Supplier", "Amount", "Project"
        ])
        
        # Configure table styling
        self.invoices_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #e2e8f0;
                selection-background-color: #edf2f7;
            }
            QHeaderView::section {
                background-color: #f7fafc;
                padding: 15px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #2d3748;
            }
        """)
        
        header = self.invoices_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.invoices_table.setAlternatingRowColors(True)
        self.invoices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.invoices_table.setShowGrid(False)
        
        # Connect selection change to enable/disable buttons
        self.invoices_table.selectionModel().selectionChanged.connect(self.on_invoice_selection_changed)
        
        layout.addWidget(self.invoices_table)
        
        self.stacked_widget.addWidget(self.invoices_page)

    def create_expenses_page(self):
        self.expenses_page = QWidget()
        layout = QVBoxLayout(self.expenses_page)
        layout.addWidget(QLabel("Expenses (to implement)"))
        self.stacked_widget.addWidget(self.expenses_page)

    def create_reports_page(self):
        self.reports_page = QWidget()
        layout = QVBoxLayout(self.reports_page)
        layout.addWidget(QLabel("Reports (to implement)"))
        self.stacked_widget.addWidget(self.reports_page)

    def create_users_page(self):
        self.users_page = QWidget()
        layout = QVBoxLayout(self.users_page)
        layout.addWidget(QLabel("Users (to implement)"))
        self.stacked_widget.addWidget(self.users_page)

    def on_navigation_changed(self, current, previous):
        if current:
            page_name = current.data(Qt.UserRole)
            if page_name == "projects":
                self.stacked_widget.setCurrentWidget(self.projects_page)
            elif page_name == "invoices":
                self.stacked_widget.setCurrentWidget(self.invoices_page)
            elif page_name == "expenses":
                self.stacked_widget.setCurrentWidget(self.expenses_page)
            elif page_name == "reports":
                self.stacked_widget.setCurrentWidget(self.reports_page)
            elif page_name == "users":
                self.stacked_widget.setCurrentWidget(self.users_page)
    
    def load_data(self):
        try:
            conn = create_connection()
            if not conn:
                QMessageBox.warning(self, "Error", "Unable to connect to database")
                return
            
            # Load projects
            projects = read_projets(conn)
            self.display_projects_table(projects)
            
            # Load invoices
            self.load_invoices(conn)
            
            conn.close()
            self.status_bar.showMessage(f"Data updated - {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error loading data:\n{str(e)}")

    def display_projects_table(self, projects):
        if not projects:
            self.projects_table.setRowCount(0)
            return

        self.projects_table.setRowCount(len(projects))
        
        # Store project IDs for later use
        self.project_ids = []

        for row, project_tuple in enumerate(projects):
            # Store project ID
            self.project_ids.append(project_tuple[0])
            
            nom_projet = project_tuple[1] if project_tuple[1] else 'N/A'
            budget_max = project_tuple[4] if project_tuple[4] else 0
            montant_investi = project_tuple[5] if project_tuple[5] else 0

            # Name
            self.projects_table.setItem(row, 0, QTableWidgetItem(nom_projet))

            # Budget
            self.projects_table.setItem(row, 1, QTableWidgetItem(format_currency(budget_max)))

            # Remaining
            reste_budget = budget_max - montant_investi
            self.projects_table.setItem(row, 2, QTableWidgetItem(format_currency(reste_budget)))

            # Status badge
            pourcentage = (montant_investi / budget_max * 100) if budget_max > 0 else 0
            if reste_budget < 0:
                status = "Over Budget"
                bg_color = "#e53e3e"
            elif pourcentage >= 80:
                status = "In Progress"
                bg_color = "#d69e2e"
            elif montant_investi == 0:
                status = "Completed"
                bg_color = "#3182ce"
            else:
                status = "Active"
                bg_color = "#38a169"

            status_label = QLabel(status)
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setStyleSheet(f"""
                background-color: {bg_color};
                color: white;
                padding: 6px 12px;
                border-radius: 12px;
                font-weight: bold;
            """)
            self.projects_table.setCellWidget(row, 3, status_label)
    
    def on_project_double_clicked(self, row, column):
        """Handle double-click on project row to show details"""
        if row < len(self.project_ids):
            project_id = self.project_ids[row]
            self.view_project_details(project_id)
    
    def load_invoices(self, conn):
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT fc.id_facture_charge, fc.date_facture, fc.fournisseur, 
                       fc.montant_total, p.nom_projet
                FROM FactureCharge fc
                JOIN Projet p ON fc.id_projet = p.id_projet
                ORDER BY fc.date_facture DESC
            """)
            invoices = cursor.fetchall()
            self.invoices_table.setRowCount(len(invoices))
            
            # Store invoice IDs for later use (hidden from user)
            self.invoice_ids = []
            
            for row, invoice in enumerate(invoices):
                # Store the actual ID for later use
                self.invoice_ids.append(invoice[0])
                
                # Show row number instead of ID
                self.invoices_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                self.invoices_table.setItem(row, 1, QTableWidgetItem(format_date(invoice[1])))
                self.invoices_table.setItem(row, 2, QTableWidgetItem(invoice[2]))
                self.invoices_table.setItem(row, 3, QTableWidgetItem(format_currency(invoice[3])))
                self.invoices_table.setItem(row, 4, QTableWidgetItem(invoice[4]))
        except Exception as e:
            print(f"Error loading invoices: {e}")
    
    def create_new_project(self):
        if show_project_form(parent=self):
            self.load_data()

    def on_invoice_selection_changed(self):
        """Enable/disable invoice action buttons based on selection"""
        selected_rows = self.invoices_table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        
        self.edit_invoice_btn.setEnabled(has_selection)
        self.delete_invoice_btn.setEnabled(has_selection)
    
    def edit_invoice(self):
        """Edit selected invoice"""
        selected_rows = self.invoices_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if row < len(self.invoice_ids):
            invoice_id = self.invoice_ids[row]
            # TODO: Implement edit invoice form
            QMessageBox.information(self, "Edit Invoice", f"Edit invoice ID: {invoice_id}")
    
    def delete_invoice(self):
        """Delete selected invoice"""
        selected_rows = self.invoices_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if row < len(self.invoice_ids):
            invoice_id = self.invoice_ids[row]
            
            reply = QMessageBox.question(self, "Delete Invoice", 
                                       "Are you sure you want to delete this invoice?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                try:
                    conn = create_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM FactureCharge WHERE id_facture_charge = ?", (invoice_id,))
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, "Success", "Invoice deleted successfully")
            self.load_data()  # Refresh data
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete invoice: {str(e)}")
    
    def create_new_invoice(self):
        if show_invoice_form(parent=self):
            self.load_data()
    
    def view_project_details(self, project_id):
        """View detailed information for a specific project"""
        try:
            conn = create_connection()
            cursor = conn.cursor()
            
            # Get project details
            cursor.execute("SELECT * FROM Projet WHERE id_projet = ?", (project_id,))
            project = cursor.fetchone()
            
            if not project:
                QMessageBox.warning(self, "Error", "Project not found")
                return
            
            # Get project invoices
            cursor.execute("""
                SELECT fc.id_facture_charge, fc.date_facture, fc.fournisseur, fc.montant_total
                FROM FactureCharge fc
                WHERE fc.id_projet = ?
                ORDER BY fc.date_facture DESC
            """, (project_id,))
            invoices = cursor.fetchall()
            
            conn.close()
            
            # Create project details dialog
            self.show_project_details_dialog(project, invoices)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load project details: {str(e)}")
    
    def show_project_details_dialog(self, project, invoices):
        """Show project details in a dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Project Details: {project[1]}")
        dialog.setModal(True)
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Project info
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"<h2>{project[1]}</h2>"))
        info_layout.addWidget(QLabel(f"<b>Budget:</b> {format_currency(project[4])}"))
        info_layout.addWidget(QLabel(f"<b>Invested:</b> {format_currency(project[5])}"))
        info_layout.addWidget(QLabel(f"<b>Remaining:</b> {format_currency(project[4] - project[5])}"))
        
        layout.addLayout(info_layout)
        
        # Invoices table
        layout.addWidget(QLabel("<h3>Project Invoices</h3>"))
        
        invoices_table = QTableWidget()
        invoices_table.setColumnCount(4)
        invoices_table.setHorizontalHeaderLabels(["#", "Date", "Supplier", "Amount"])
        
        invoices_table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            invoices_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            invoices_table.setItem(row, 1, QTableWidgetItem(format_date(invoice[1])))
            invoices_table.setItem(row, 2, QTableWidgetItem(invoice[2]))
            invoices_table.setItem(row, 3, QTableWidgetItem(format_currency(invoice[3])))
        
        header = invoices_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        invoices_table.setAlternatingRowColors(True)
        
        layout.addWidget(invoices_table)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
