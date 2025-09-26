from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QStatusBar, QFrame,
    QStackedWidget, QListWidget, QListWidgetItem, QPushButton, QLabel,
    QDialog, QComboBox, QLineEdit, QDateEdit, QProgressDialog, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QColor
from datetime import datetime

from app.db import create_connection, read_projets, read_lignes_charge_by_facture
from app.utils import format_currency, format_date
from app.gui.project_form import show_project_form
from app.gui.invoice_form import show_invoice_form, show_invoice_details


class MainApplicationWindow(QMainWindow):
    """Main application window with modern dashboard design"""
    
    def __init__(self, user_data=None):
        super().__init__()
        self.current_page = "projects"
        self.user_data = user_data or {}
        self.user_role = self.user_data.get('role', 'Employe')  # Default to Employee
        self.username = self.user_data.get('username', 'User')
        
        # Initialize invoice status storage (in a real app, this would be in database)
        self.invoice_statuses = {}  # Dictionary to store invoice_id -> status mapping

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
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #31343a;
                border: none;
            }status_label.setStyleSheet
        """)

        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo area
        logo_frame = QFrame()
        logo_frame.setFixedHeight(200)
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        logo_path = r"C:\Project\v0.3\Project-PFA\Images\LogoX.png"
        pixmap = QPixmap(logo_path)
        pixmap = pixmap.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background: #e5e7eb; min-height: 2px; max-height: 2px; margin: 12px 0 0 0;")
        logo_layout.addWidget(separator)

        layout.addWidget(logo_frame)

        # Add more space before menu to push it down
        menu_spacer = QWidget()
        menu_spacer.setFixedHeight(90)
        layout.addWidget(menu_spacer)

        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav_list.setFixedHeight(320)
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: #31343a;
                border: none;
                color: #e2e8f0;
                font-size: 15px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 14px 24px;
                border: none;
                border-radius: 8px;
                margin: 6px 10px;
            }
            QListWidget::item:selected {
                background-color: #ed8936;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #23272f;
                color: #e2e8f0;
            }
        """)

        # Define navigation items based on role
        all_nav_items = [
            ("🏠", "Projects"),
            ("📄", "Invoices"),
            ("", "Reports"),
            ("👤", "Users")
        ]
        
        # Filter navigation items based on user role
        if self.user_role == "Directeur":
            nav_items = all_nav_items  # Directors get full access
        else:  # Employee
            nav_items = [
                ("🏠", "Projects"),
                ("📄", "Invoices"),
                ("📈", "Reports")
                # Users management is Director-only
            ]
        
        for icon, text in nav_items:
            item = QListWidgetItem(f"{icon}  {text}")
            item.setData(Qt.UserRole, text.lower())
            self.nav_list.addItem(item)
        self.nav_list.setCurrentRow(0)  # Start with Projects page (first item)
        self.nav_list.currentItemChanged.connect(self.on_navigation_changed)

        layout.addWidget(self.nav_list)

        # Add more stretch after menu to push it down
        layout.addStretch(2)

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

        # Header box (gray background, full width)
        header_box = QFrame()
        header_box.setStyleSheet("""
            QFrame {
            QFrame {
                background-color: #f7f7f7;
                border-radius: 0;
                border: none;
                margin: 0;
                padding: 0;
            }
        """)
        header_box_layout = QHBoxLayout(header_box)
        header_box_layout.setContentsMargins(40, 24, 40, 24)
        welcome_label = QLabel(f"Welcome, {self.user_role}")
        welcome_label.setFont(QFont("Arial", 18, QFont.Bold))
        welcome_label.setStyleSheet("color: #222; letter-spacing: 0.5px;")
        header_box_layout.addWidget(welcome_label)
        header_box_layout.addStretch()
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
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
        logout_btn.clicked.connect(self.logout)
        header_box_layout.addWidget(logout_btn)
        
        layout.addWidget(header_box)

        # Title + Add button
        title_layout = QHBoxLayout()
        title_label = QLabel("Active Projects")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2d3748;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # Add Project button (Director only)
        if self.user_role == "Directeur":
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
                font-size: 15px;
            }
            QHeaderView::section {
                background-color: #f7f7f7;
                color: #999999;
                padding: 18px 0 18px 0;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                font-size: 17px;
                letter-spacing: 0.5px;
            }
            QTableWidget::item {
                padding: 12px 24px;
                font-size: 15px;
            }
            QTableWidget::item:selected {
                background: #f1f5f9;
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

    def logout(self):
        """Handle logout - return to login screen instead of quitting"""
        from PyQt5.QtWidgets import QApplication
        
        # Close current window
        self.close()
        
        # Show login dialog
        from app.gui.login import LoginSignupDialog
        login_dialog = LoginSignupDialog()
        
        if login_dialog.exec_() == login_dialog.Accepted:
            # Login successful, get user data and show main window
            user_data = getattr(login_dialog, 'user_data', None)
            # Create new main window
            new_main_window = MainApplicationWindow(user_data)
            new_main_window.show()
        else:
            # If login is cancelled, quit the application
            QApplication.instance().quit()

    def create_invoices_page(self):
        self.invoices_page = QWidget()
        layout = QVBoxLayout(self.invoices_page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header with title and Add Invoice button
        header_layout = QHBoxLayout()
        title_label = QLabel("Invoices")
        title_label.setFont(QFont("Arial", 32, QFont.Bold))
        title_label.setStyleSheet("color: #2d3748;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add Invoice button (matching the orange design)
        self.add_invoice_btn = QPushButton("Add Invoice")
        self.add_invoice_btn.setStyleSheet("""
            QPushButton {
                background-color: #ed7734;
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
        self.add_invoice_btn.clicked.connect(self.create_new_invoice)
        header_layout.addWidget(self.add_invoice_btn)
        
        layout.addLayout(header_layout)
        
        # Invoices table with new structure
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(6)
        self.invoices_table.setHorizontalHeaderLabels([
            "Invoice ID", "Supplier", "Date", "Status", "Actions", ""
        ])
        
        # Configure table styling to match the design
        self.invoices_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                gridline-color: #e2e8f0;
                selection-background-color: #f7fafc;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 16px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: 600;
                color: #374151;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f5f9;
            }
        """)
        
        header = self.invoices_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Invoice ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Supplier  
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(3, QHeaderView.Fixed)             # Status - fixed width
        header.setSectionResizeMode(4, QHeaderView.Fixed)             # Actions - fixed width
        header.setSectionResizeMode(5, QHeaderView.Fixed)             # Hidden spacer
        
        # Set specific widths for Status and Actions columns
        self.invoices_table.setColumnWidth(3, 120)  # Status column
        self.invoices_table.setColumnWidth(4, 140)  # Actions column (wider for both buttons)
        self.invoices_table.setColumnWidth(5, 0)    # Hide the last column
        
        self.invoices_table.setAlternatingRowColors(False)  # Disable alternating colors for cleaner look
        self.invoices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.invoices_table.setShowGrid(False)
        self.invoices_table.verticalHeader().setVisible(False)
        self.invoices_table.setRowHeight(0, 50)  # Set default row height
        
        # Connect double-click to show invoice details
        self.invoices_table.doubleClicked.connect(self.show_invoice_details)
        
        layout.addWidget(self.invoices_table)
        
        self.stacked_widget.addWidget(self.invoices_page)

    def create_reports_page(self):
        """Create the reports page with PDF generation functionality"""
        self.reports_page = QWidget()
        layout = QVBoxLayout(self.reports_page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Header
        title = QLabel("Reports")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2d3748; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Main content container
        main_container = QWidget()
        main_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Select Project Section
        project_section = QVBoxLayout()
        project_label = QLabel("Select Project")
        project_label.setFont(QFont("Arial", 16, QFont.Bold))
        project_label.setStyleSheet("color: #2d3748; margin-bottom: 10px;")
        project_section.addWidget(project_label)
        
        self.project_combo = QComboBox()
        self.project_combo.setStyleSheet("""
            QComboBox {
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;
            }
            QComboBox:focus {
                border-color: #ed8936;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 2px;
                border-left-color: #e2e8f0;
                border-left-style: solid;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QComboBox::down-arrow {
                image: none;
                border-style: solid;
                border-width: 3px 3px 0px 3px;
                border-color: transparent transparent #6b7280 transparent;
                width: 0px;
                height: 0px;
            }
        """)
        self.load_projects_for_reports()
        project_section.addWidget(self.project_combo)
        main_layout.addLayout(project_section)
        
        # Report Type Section
        report_type_section = QVBoxLayout()
        report_type_label = QLabel("Report Type")
        report_type_label.setFont(QFont("Arial", 16, QFont.Bold))
        report_type_label.setStyleSheet("color: #2d3748; margin-bottom: 10px;")
        report_type_section.addWidget(report_type_label)
        
        # Report type buttons container
        report_buttons_container = QWidget()
        report_buttons_layout = QVBoxLayout(report_buttons_container)
        report_buttons_layout.setSpacing(15)
        
        # Invoice PDF button
        self.invoice_report_btn = QPushButton()
        self.invoice_report_btn.setCheckable(True)
        invoice_btn_layout = QHBoxLayout(self.invoice_report_btn)
        invoice_btn_layout.setContentsMargins(20, 15, 20, 15)
        
        invoice_icon = QLabel("📄")
        invoice_icon.setFont(QFont("Arial", 18))
        invoice_btn_layout.addWidget(invoice_icon)
        
        invoice_text = QLabel("Invoice PDF")
        invoice_text.setFont(QFont("Arial", 14))
        invoice_btn_layout.addWidget(invoice_text)
        
        invoice_btn_layout.addStretch()
        
        self.invoice_report_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                text-align: left;
                min-height: 50px;
            }
            QPushButton:hover {
                border-color: #ed8936;
                background-color: #fef5e7;
            }
            QPushButton:checked {
                border-color: #ed8936;
                background-color: #fef5e7;
            }
        """)
        report_buttons_layout.addWidget(self.invoice_report_btn)
        
        # Project Complete button
        self.complete_report_btn = QPushButton()
        self.complete_report_btn.setCheckable(True)
        complete_btn_layout = QHBoxLayout(self.complete_report_btn)
        complete_btn_layout.setContentsMargins(20, 15, 20, 15)
        
        complete_icon = QLabel("📊")
        complete_icon.setFont(QFont("Arial", 18))
        complete_btn_layout.addWidget(complete_icon)
        
        complete_text = QLabel("Project Summary")
        complete_text.setFont(QFont("Arial", 14))
        complete_btn_layout.addWidget(complete_text)
        
        complete_btn_layout.addStretch()
        
        self.complete_report_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                text-align: left;
                min-height: 50px;
            }
            QPushButton:hover {
                border-color: #ed8936;
                background-color: #fef5e7;
            }
            QPushButton:checked {
                border-color: #ed8936;
                background-color: #fef5e7;
            }
        """)
        report_buttons_layout.addWidget(self.complete_report_btn)
        
        report_type_section.addWidget(report_buttons_container)
        main_layout.addLayout(report_type_section)
        
        # Date Range Section
        date_range_section = QVBoxLayout()
        date_range_label = QLabel("Date Range")
        date_range_label.setFont(QFont("Arial", 16, QFont.Bold))
        date_range_label.setStyleSheet("color: #2d3748; margin-bottom: 10px;")
        date_range_section.addWidget(date_range_label)
        
        # Date range buttons
        date_buttons_layout = QHBoxLayout()
        date_buttons_layout.setSpacing(10)
        
        self.date_buttons = []
        date_options = [
            ("Today", "today"),
            ("This Week", "this_week"), 
            ("This Month", "this_month"),
            ("Custom Range", "custom")
        ]
        
        for text, value in date_options:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty("date_value", value)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 2px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    border-color: #ed8936;
                    background-color: #fef5e7;
                }
                QPushButton:checked {
                    border-color: #ed8936;
                    background-color: #ed8936;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, b=btn: self.select_date_range(b))
            self.date_buttons.append(btn)
            date_buttons_layout.addWidget(btn)
        
        date_buttons_layout.addStretch()
        date_range_section.addLayout(date_buttons_layout)
        
        # Custom date range inputs (initially hidden)
        self.custom_date_container = QWidget()
        custom_date_layout = QHBoxLayout(self.custom_date_container)
        custom_date_layout.setContentsMargins(0, 10, 0, 0)
        
        from_label = QLabel("From:")
        from_label.setStyleSheet("font-weight: bold; color: #4a5568;")
        custom_date_layout.addWidget(from_label)
        
        from PyQt5.QtWidgets import QDateEdit
        from PyQt5.QtCore import QDate
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setStyleSheet("""
            QDateEdit {
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 13px;
            }
            QDateEdit:focus {
                border-color: #ed8936;
            }
        """)
        custom_date_layout.addWidget(self.start_date_edit)
        
        to_label = QLabel("To:")
        to_label.setStyleSheet("font-weight: bold; color: #4a5568; margin-left: 20px;")
        custom_date_layout.addWidget(to_label)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setStyleSheet("""
            QDateEdit {
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 13px;
            }
            QDateEdit:focus {
                border-color: #ed8936;
            }
        """)
        custom_date_layout.addWidget(self.end_date_edit)
        
        custom_date_layout.addStretch()
        self.custom_date_container.setVisible(False)
        
        date_range_section.addWidget(self.custom_date_container)
        main_layout.addLayout(date_range_section)
        
        # Generate PDF Button
        generate_btn = QPushButton("📥  Generate PDF")
        generate_btn.setFont(QFont("Arial", 16, QFont.Bold))
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #ed8936;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dd6b20;
            }
            QPushButton:pressed {
                background-color: #c05621;
            }
        """)
        generate_btn.clicked.connect(self.generate_pdf_report)
        main_layout.addWidget(generate_btn)
        
        layout.addWidget(main_container)
        
        # Connect report type buttons
        self.invoice_report_btn.clicked.connect(lambda: self.select_report_type('invoice'))
        self.complete_report_btn.clicked.connect(lambda: self.select_report_type('complete'))
        
        # Set default selections
        self.invoice_report_btn.setChecked(True)
        self.date_buttons[0].setChecked(True)  # Today
        
        self.stacked_widget.addWidget(self.reports_page)

    def create_users_page(self):
        """Create the users management page"""
        self.users_page = QWidget()
        layout = QVBoxLayout(self.users_page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Header section
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("User Management")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2d3748; margin-bottom: 10px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Add User and Export Data buttons (Director only)
        if self.user_role == "Directeur":
            add_user_btn = QPushButton("Add User")
            add_user_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ed8936;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #dd6b20;
                }
            """)
            add_user_btn.clicked.connect(self.add_user)
            header_layout.addWidget(add_user_btn)
        
        layout.addLayout(header_layout)
        
        # Search and filter section
        search_filter_layout = QHBoxLayout()
        
        # Search box
        self.user_search_input = QLineEdit()
        self.user_search_input.setPlaceholderText("🔍 Search")
        self.user_search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                min-width: 250px;
            }
            QLineEdit:focus {
                border-color: #ed8936;
            }
        """)
        self.user_search_input.textChanged.connect(self.filter_users)
        search_filter_layout.addWidget(self.user_search_input)
        
        # Role filter buttons
        all_roles_btn = QPushButton("All Roles")
        all_roles_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #6b7280;
                border: 2px solid #e2e8f0;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                margin-left: 20px;
            }
            QPushButton:hover {
                background-color: #ed8936;
                color: white;
                border-color: #ed8936;
            }
        """)
        all_roles_btn.clicked.connect(lambda: self.filter_users_by_role(""))
        search_filter_layout.addWidget(all_roles_btn)
        
        employee_btn = QPushButton("Employee")
        employee_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #6b7280;
                border: 2px solid #e2e8f0;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #ed8936;
                color: white;
                border-color: #ed8936;
            }
        """)
        employee_btn.clicked.connect(lambda: self.filter_users_by_role("Employe"))
        search_filter_layout.addWidget(employee_btn)
        
        director_btn = QPushButton("Director")
        director_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #6b7280;
                border: 2px solid #e2e8f0;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #ed8936;
                color: white;
                border-color: #ed8936;
            }
        """)
        director_btn.clicked.connect(lambda: self.filter_users_by_role("Directeur"))
        search_filter_layout.addWidget(director_btn)
        
        search_filter_layout.addStretch()
        layout.addLayout(search_filter_layout)
        
        # User Accounts section
        accounts_label = QLabel("User Accounts")
        accounts_label.setFont(QFont("Arial", 18, QFont.Bold))
        accounts_label.setStyleSheet("color: #4a5568; margin: 20px 0 10px 0;")
        layout.addWidget(accounts_label)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["User ID", "Username", "Role", "Actions"])
        
        # Table styling
        self.users_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
                gridline-color: #f0f0f0;
                selection-background-color: #f8fafc;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 15px 10px;
                border: none;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #f8fafc;
            }
            QHeaderView::section {
                background-color: #f7fafc;
                font-weight: bold;
                font-size: 14px;
                color: #4a5568;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 15px 10px;
                text-align: left;
            }
        """)
        
        # Table configuration
        self.users_table.setAlternatingRowColors(False)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setShowGrid(False)
        
        # Column widths
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # User ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Username
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Role
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Actions
        
        layout.addWidget(self.users_table)
        
        # Add New User button (bottom) - Director only
        if self.user_role == "Directeur":
            bottom_layout = QHBoxLayout()
            add_new_user_btn = QPushButton("Add New User")
            add_new_user_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ed8936;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #dd6b20;
                }
            """)
            add_new_user_btn.clicked.connect(self.add_user)
            bottom_layout.addWidget(add_new_user_btn)
            bottom_layout.addStretch()
            layout.addLayout(bottom_layout)
        
        self.stacked_widget.addWidget(self.users_page)
        
        # Load users data
        self.load_users_data()

    def on_navigation_changed(self, current, previous):
        if current:
            page_name = current.data(Qt.UserRole)
            if page_name == "projects":
                self.stacked_widget.setCurrentWidget(self.projects_page)
            elif page_name == "invoices":
                self.stacked_widget.setCurrentWidget(self.invoices_page)
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
        self.project_ids = []

        for row, project_tuple in enumerate(projects):
            self.project_ids.append(project_tuple[0])
            nom_projet = project_tuple[1] if project_tuple[1] else 'N/A'
            budget_max = project_tuple[4] if project_tuple[4] else 0
            montant_investi = project_tuple[5] if project_tuple[5] else 0

            # Name
            item_name = QTableWidgetItem(nom_projet)
            item_name.setFont(QFont("Arial", 14))
            item_name.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.projects_table.setItem(row, 0, item_name)

            # Budget
            item_budget = QTableWidgetItem(format_currency(budget_max))
            item_budget.setFont(QFont("Arial", 14))
            item_budget.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.projects_table.setItem(row, 1, item_budget)

            # Remaining
            reste_budget = budget_max - montant_investi
            item_remain = QTableWidgetItem(format_currency(reste_budget))
            item_remain.setFont(QFont("Arial", 14))
            item_remain.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.projects_table.setItem(row, 2, item_remain)

            # Status badge - Use database status instead of calculated status
            db_status = project_tuple[6] if len(project_tuple) > 6 and project_tuple[6] else 'Active'
            
            # Map database status to display colors
            if db_status == "Completed":
                status = "Completed"
                bg_color = "#6b7280"  # Gray for completed
                text_color = "white"
            elif db_status == "In Progress":
                status = "In Progress" 
                bg_color = "#f59e0b"  # Orange/Yellow for in progress
                text_color = "white"
            else:  # Active or any other status
                status = "Active"
                bg_color = "#10b981"  # Green for active
                text_color = "white"

            # Create status widget
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(10, 10, 10, 10)  # More generous margins
            status_layout.setAlignment(Qt.AlignCenter)
            
            status_label = QLabel(status)
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_color};
                    color: {text_color};
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 11px;
                    padding: 5px 15px;
                    min-width: 80px;
                    max-width: 120px;
                }}
            """)
            
            status_layout.addWidget(status_label)
            self.projects_table.setCellWidget(row, 3, status_widget)
            
            # Set row height for better appearance
            self.projects_table.setRowHeight(row, 70)  # Increased height even more

        # Configure column widths
        self.projects_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)      # Project Name
        self.projects_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Budget
        self.projects_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Remaining  
        self.projects_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)  # Status - Fixed width
        self.projects_table.setColumnWidth(3, 150)  # Increased width for status column

        # Table style: subtle row striping, no grid lines
        self.projects_table.setAlternatingRowColors(False)
        self.projects_table.setStyleSheet(self.projects_table.styleSheet() + """
            QTableWidget {
                border-radius: 18px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #e2e8f0;
                font-size: 15px;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background: #f1f5f9;
            }
        """)
        self.projects_table.setShowGrid(False)
        self.projects_table.verticalHeader().setVisible(False)
        self.projects_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background: #f7fafc;
                font-weight: bold;
                font-size: 16px;
                color: #2d3748;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 12px 0;
            }
        """)
    
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
                       fc.montant_total, p.nom_projet, fc.status
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
                
                # Column 0: Invoice ID (formatted like INV-2024-001)
                invoice_id = f"INV-2024-{str(invoice[0]).zfill(3)}"
                id_item = QTableWidgetItem(invoice_id)
                id_item.setFont(QFont("Arial", 12, QFont.Bold))
                self.invoices_table.setItem(row, 0, id_item)
                
                # Column 1: Supplier
                supplier_item = QTableWidgetItem(invoice[2])  # Supplier name
                self.invoices_table.setItem(row, 1, supplier_item)
                
                # Column 2: Date
                date_item = QTableWidgetItem(format_date(invoice[1]))
                self.invoices_table.setItem(row, 2, date_item)
                
                # Column 3: Status with colored indicator
                status_widget = QWidget()
                status_layout = QHBoxLayout(status_widget)
                status_layout.setContentsMargins(12, 8, 12, 8)
                status_layout.setSpacing(6)
                
                # Status dot
                status_dot = QLabel("●")
                status_dot.setStyleSheet("font-size: 14px;")
                
                # Status text
                status_text = QLabel()
                status_text.setFont(QFont("Arial", 11, QFont.Bold))
                
                # Use status from database (index 5 in our query)
                status_name = invoice[5] if len(invoice) > 5 and invoice[5] else "Pending"
                
                # Set color based on status
                status_colors = {
                    "Paid": "#22c55e",      # Green
                    "Pending": "#eab308",   # Yellow
                    "Overdue": "#ef4444"    # Red
                }
                status_color = status_colors.get(status_name, "#eab308")
                
                status_dot.setStyleSheet(f"color: {status_color}; font-size: 14px;")
                status_text.setText(status_name)
                status_text.setStyleSheet(f"color: {status_color}; font-weight: bold; font-size: 11px;")
                
                status_layout.addWidget(status_dot)
                status_layout.addWidget(status_text)
                status_layout.addStretch()
                
                self.invoices_table.setCellWidget(row, 3, status_widget)
                
                # Column 4: Action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(6, 4, 6, 4)
                actions_layout.setSpacing(4)
                
                # Center the delete button
                actions_layout.addStretch()  # Add stretch before button
                
                # Delete button only (Director only)
                if self.user_role == "Directeur":
                    delete_btn = QPushButton("Delete")
                    delete_btn.setFixedSize(55, 28)  # Fixed size to prevent cutoff
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #ef4444;
                            color: white;
                            border: none;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 11px;
                        }
                        QPushButton:hover {
                            background-color: #dc2626;
                        }
                    """)
                    delete_btn.clicked.connect(lambda checked, r=row: self.delete_invoice_at_row(r))
                    actions_layout.addWidget(delete_btn)
                else:
                    # Show read-only label for Employees
                    read_only_label = QLabel("Read Only")
                    read_only_label.setStyleSheet("""
                        QLabel {
                            color: #6b7280;
                            font-style: italic;
                            font-size: 11px;
                        }
                    """)
                    actions_layout.addWidget(read_only_label)
                
                actions_layout.addStretch()  # Add stretch after button
                
                self.invoices_table.setCellWidget(row, 4, actions_widget)
                
                # Set row height for better appearance
                self.invoices_table.setRowHeight(row, 60)
        except Exception as e:
            print(f"Error loading invoices: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load invoices: {str(e)}")
    
    def create_new_project(self):
        if self.user_role != "Directeur":
            QMessageBox.warning(self, "Access Denied", "Only Directors can create new projects.")
            return
        if show_project_form(parent=self):
            self.load_data()

    def edit_invoice_at_row(self, row):
        """Edit invoice at specific row"""
        try:
            if row < len(self.invoice_ids):
                invoice_id = self.invoice_ids[row]
                print(f"Edit invoice {invoice_id} at row {row}")
                # You can implement the edit functionality here
                self.edit_invoice()
        except Exception as e:
            print(f"Error editing invoice at row {row}: {e}")

    def delete_invoice_at_row(self, row):
        """Delete invoice at specific row"""
        if self.user_role != "Directeur":
            QMessageBox.warning(self, "Access Denied", "Only Directors can delete invoices.")
            return
        try:
            if row < len(self.invoice_ids):
                invoice_id = self.invoice_ids[row]
                print(f"Delete invoice {invoice_id} at row {row}")
                # Set the selection to this row and call delete
                self.invoices_table.selectRow(row)
                self.delete_invoice()
        except Exception as e:
            print(f"Error deleting invoice at row {row}: {e}")
    
    def update_invoice_status(self, invoice_id, new_status):
        """Update the status of an invoice"""
        try:
            self.invoice_statuses[invoice_id] = new_status
            print(f"Updated invoice {invoice_id} status to {new_status}")
            # Refresh the table to show the new status
            self.load_data()
        except Exception as e:
            print(f"Error updating invoice status: {e}")
    
    def update_project_status(self, project_id, new_status):
        """Update project status and refresh the table"""
        try:
            # First, update the database
            from app.db import create_connection, update_projet_status
            
            conn = create_connection()
            if conn:
                update_projet_status(conn, project_id, new_status)
                conn.close()
                print(f"Updated project {project_id} status to {new_status} in database")
            
            # Then update the UI
            # Find and update the specific row in the projects table
            for row in range(self.projects_table.rowCount()):
                if row < len(self.project_ids) and self.project_ids[row] == project_id:
                    # Update the status widget with new color
                    status_colors = {
                        'Active': '#10b981',      # Green
                        'In Progress': '#f59e0b', # Orange
                        'Completed': '#6b7280'    # Gray
                    }
                    
                    bg_color = status_colors.get(new_status, '#6b7280')
                    
                    # Create new status widget
                    status_widget = QWidget()
                    status_layout = QHBoxLayout(status_widget)
                    status_layout.setContentsMargins(10, 10, 10, 10)
                    status_layout.setAlignment(Qt.AlignCenter)
                    
                    status_label = QLabel(new_status)
                    status_label.setAlignment(Qt.AlignCenter)
                    status_label.setStyleSheet(f"""
                        QLabel {{
                            background-color: {bg_color};
                            color: white;
                            border-radius: 8px;
                            font-weight: bold;
                            font-size: 11px;
                            padding: 5px 15px;
                            min-width: 80px;
                            max-width: 120px;
                        }}
                    """)
                    
                    status_layout.addWidget(status_label)
                    self.projects_table.setCellWidget(row, 3, status_widget)
                    break
                    
        except Exception as e:
            print(f"Error updating project status: {e}")

    def on_invoice_selection_changed(self):
        """Enable/disable invoice action buttons based on selection"""
        selected_rows = self.invoices_table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        
        # Only enable delete button - edit functionality removed
        if hasattr(self, 'delete_invoice_btn'):
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
        if self.user_role != "Directeur":
            QMessageBox.warning(self, "Access Denied", "Only Directors can delete invoices.")
            return
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
                    QMessageBox.critical(self, "Error", f"Error deleting invoice: {str(e)}")
    
    def show_invoice_details(self, index):
        """Show invoice details dialog when double-clicking an invoice"""
        row = index.row()
        if row < self.invoices_table.rowCount() and row < len(self.invoice_ids):
            # Get invoice data from the new table structure
            invoice_id = self.invoice_ids[row]
            current_status = self.invoice_statuses.get(invoice_id, 'Pending')  # Get current status
            
            invoice_data = {
                'id': invoice_id,
                'number': self.invoices_table.item(row, 0).text() if self.invoices_table.item(row, 0) else '',  # Invoice ID 
                'supplier': self.invoices_table.item(row, 1).text() if self.invoices_table.item(row, 1) else '',  # Supplier
                'date': self.invoices_table.item(row, 2).text() if self.invoices_table.item(row, 2) else '',    # Date
                'amount': 'DH10,000.00',  # Placeholder amount - you can get this from database
                'status': current_status  # Pass current status
            }
            
            # Get expense lines from database
            expense_lines = []
            try:
                conn = create_connection()
                if conn:
                    expense_lines = read_lignes_charge_by_facture(conn, invoice_id)
                    conn.close()
            except Exception as e:
                print(f"Error fetching expense lines: {e}")
            
            # Show the invoice details dialog with expense lines
            show_invoice_details(invoice_data, expense_lines, self)
    
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
            
            conn.close()
            
            # Convert project tuple to dictionary
            project_data = {
                'id_projet': project[0],
                'nom_projet': project[1],
                'date_estimation': project[2],
                'date_lancement': project[3],
                'budget_max': project[4],
                'montant_investi': project[5],
                'status': project[6] if len(project) > 6 else 'Active'
            }
            
            # Show project details dialog
            from app.gui.project_details import show_project_details
            show_project_details(project_data, self, self.user_role)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load project details: {str(e)}")
    
    def show_project_details_dialog(self, project, invoices):
        """Show project details in a dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Invoice Details")
        dialog.setModal(True)
        dialog.resize(900, 600)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(18)

        # Top info row
        info_row = QHBoxLayout()
        info_row.setSpacing(40)
        info_row.addWidget(QLabel(f"<b>Invoice Number:</b> {project[0] if project else ''}"))
        info_row.addWidget(QLabel(f"<b>Supplier Name:</b> {project[2] if project else ''}"))
        info_row.addWidget(QLabel(f"<b>Invoice Date:</b> {format_date(project[3]) if project else ''}"))
        info_row.addWidget(QLabel(f"<b>Total Amount:</b> <span style='color:#ed8936;font-weight:bold;'>{format_currency(project[4]) if project else ''}</span>"))
        layout.addLayout(info_row)

        # Edit and Mark as Paid buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ed8936;
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #dd6b20;
            }
        """)
        btn_row.addWidget(edit_btn)
        mark_paid_btn = QPushButton("Mark as Paid")
        mark_paid_btn.setStyleSheet(edit_btn.styleSheet())
        btn_row.addWidget(mark_paid_btn)
        layout.addLayout(btn_row)

        # Expense table
        expense_table = QTableWidget()
        expense_table.setColumnCount(4)
        expense_table.setHorizontalHeaderLabels(["Expense Lines", "Unit Price", "Quantity", "Total"])
        expense_table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            expense_table.setItem(row, 0, QTableWidgetItem(invoice[2]))
            expense_table.setItem(row, 1, QTableWidgetItem(format_currency(invoice[3])))
            expense_table.setItem(row, 2, QTableWidgetItem(str(1)))
            expense_table.setItem(row, 3, QTableWidgetItem("0"))
        expense_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #e2e8f0;
                font-size: 15px;
            }
            QHeaderView::section {
                background-color: #f7f7f7;
                color: #222;
                padding: 14px 0 14px 0;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                font-size: 16px;
            }
            QTableWidget::item {
                padding: 10px 18px;
                font-size: 15px;
            }
        """)
        expense_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(expense_table)

        # Add Expense Line button
        add_expense_btn = QPushButton("Add Expense Line")
        add_expense_btn.setStyleSheet(edit_btn.styleSheet())
        layout.addWidget(add_expense_btn)

        # Summary row
        summary_row = QHBoxLayout()
        summary_row.addStretch()
        summary_row.addWidget(QLabel("Subtotal:"))
        summary_row.addWidget(QLabel("Tax (10%):"))
        total_due_label = QLabel("Total Due")
        total_due_label.setStyleSheet("background-color:#ed8936;color:white;font-weight:bold;padding:8px 24px;border-radius:6px;font-size:15px;")
        summary_row.addWidget(total_due_label)
        layout.addLayout(summary_row)

        dialog.exec_()

    # User Management Methods
    def load_users_data(self):
        """Load users data into the table"""
        try:
            from app.db import get_all_users
            users = get_all_users()
            if not users:
                self.users_table.setRowCount(0)
                return
            
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                # Assuming user format: (id_user, username, password, role)
                user_id = f"USR-{user[0]:03d}" if user[0] else "USR-001"
                username = user[1] if len(user) > 1 else "N/A"
                role = user[3] if len(user) > 3 else "Employe"  # Default to correct role name
                
                # User ID
                id_item = QTableWidgetItem(user_id)
                id_item.setFont(QFont("Arial", 13, QFont.Bold))
                self.users_table.setItem(row, 0, id_item)
                
                # Username
                username_item = QTableWidgetItem(username)
                username_item.setFont(QFont("Arial", 13))
                self.users_table.setItem(row, 1, username_item)
                
                # Role
                role_item = QTableWidgetItem(role)
                role_item.setFont(QFont("Arial", 13))
                role_color = "#10b981" if role == "Directeur" else "#6b7280"  # Use correct role name
                role_item.setForeground(QColor(role_color))
                self.users_table.setItem(row, 2, role_item)
                
                # Actions
                actions_widget = self.create_user_actions_widget(user[0], row)
                self.users_table.setCellWidget(row, 3, actions_widget)
                
                # Set row height
                self.users_table.setRowHeight(row, 65)
                
        except Exception as e:
            print(f"Error loading users: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")
    
    def create_user_actions_widget(self, user_id, row):
        """Create actions widget for user row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)
        
        # Only show action buttons for Directors
        if self.user_role == "Directeur":
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(50, 32)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            edit_btn.clicked.connect(lambda: self.edit_user_role(user_id, row))
            layout.addWidget(edit_btn)
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setFixedSize(55, 32)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            delete_btn.clicked.connect(lambda: self.delete_user(user_id, row))
            layout.addWidget(delete_btn)
        else:
            # Show read-only label for Employees
            read_only_label = QLabel("Read Only")
            read_only_label.setStyleSheet("""
                QLabel {
                    color: #6b7280;
                    font-style: italic;
                    font-size: 12px;
                    padding: 8px;
                }
            """)
            layout.addWidget(read_only_label)
        
        return widget
    
    def filter_users(self):
        """Filter users based on search text"""
        search_text = self.user_search_input.text().lower()
        
        for row in range(self.users_table.rowCount()):
            show_row = False
            
            # Check if search text matches any column
            for col in range(3):  # Skip Actions column
                item = self.users_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            
            self.users_table.setRowHidden(row, not show_row)
    
    def filter_users_by_role(self, role):
        """Filter users by role"""
        for row in range(self.users_table.rowCount()):
            role_item = self.users_table.item(row, 2)
            if role_item:
                if not role or role_item.text() == role:
                    self.users_table.setRowHidden(row, False)
                else:
                    self.users_table.setRowHidden(row, True)
    
    def add_user(self):
        """Show add user dialog"""
        if self.user_role != "Directeur":
            QMessageBox.warning(self, "Access Denied", "Only Directors can add users.")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New User")
        dialog.setModal(True)
        dialog.setFixedSize(450, 350)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Add New User")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2d3748; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Username field
        username_layout = QVBoxLayout()
        username_layout.setSpacing(8)
        username_label = QLabel("Username:")
        username_label.setFont(QFont("Arial", 14))
        username_label.setStyleSheet("color: #4a5568;")
        username_layout.addWidget(username_label)
        
        username_input = QLineEdit()
        username_input.setPlaceholderText("Enter username")
        username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #ed8936;
            }
        """)
        username_layout.addWidget(username_input)
        layout.addLayout(username_layout)
        
        # Password field
        password_layout = QVBoxLayout()
        password_layout.setSpacing(8)
        password_label = QLabel("Password:")
        password_label.setFont(QFont("Arial", 14))
        password_label.setStyleSheet("color: #4a5568;")
        password_layout.addWidget(password_label)
        
        password_input = QLineEdit()
        password_input.setPlaceholderText("Enter password")
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #ed8936;
            }
        """)
        password_layout.addWidget(password_input)
        layout.addLayout(password_layout)
        
        # Role selection
        role_layout = QVBoxLayout()
        role_layout.setSpacing(8)
        role_label = QLabel("Role:")
        role_label.setFont(QFont("Arial", 14))
        role_label.setStyleSheet("color: #4a5568;")
        role_layout.addWidget(role_label)
        
        role_combo = QComboBox()
        role_combo.addItems(["Employe", "Directeur"])  # Use database role names
        role_combo.setStyleSheet("""
            QComboBox {
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #ed8936;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 2px;
                border-left-color: #e2e8f0;
                border-left-style: solid;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)
        role_layout.addWidget(role_combo)
        layout.addLayout(role_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f7fafc;
                color: #4a5568;
                border: 2px solid #e2e8f0;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #edf2f7;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        add_btn = QPushButton("Add User")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #ed8936;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #dd6b20;
            }
        """)
        
        def handle_add_user():
            username = username_input.text().strip()
            password = password_input.text().strip()
            role = role_combo.currentText()
            
            if not username or not password:
                QMessageBox.warning(dialog, "Error", "Please fill in all fields.")
                return
            
            try:
                from app.db import add_user
                from app.auth import hash_password
                
                # Hash the password before storing
                hashed_password = hash_password(password)
                success = add_user(username, hashed_password, role)
                
                if success:
                    QMessageBox.information(dialog, "Success", f"User '{username}' added successfully!")
                    dialog.accept()
                    self.load_users_data()  # Refresh the table
                else:
                    QMessageBox.warning(dialog, "Error", "Failed to add user. Username may already exist.")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Error adding user: {str(e)}")
        
        add_btn.clicked.connect(handle_add_user)
        button_layout.addWidget(add_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def edit_user_role(self, user_id, row):
        """Edit user role dialog"""
        try:
            # Get current user data
            username_item = self.users_table.item(row, 1)
            current_role_item = self.users_table.item(row, 2)
            
            if not username_item or not current_role_item:
                return
                
            username = username_item.text()
            current_role = current_role_item.text()
            
            # Create edit dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit User Role")
            dialog.setModal(True)
            dialog.setFixedSize(400, 250)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: white;
                    border-radius: 12px;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(30, 30, 30, 30)
            layout.setSpacing(20)
            
            # Username label
            username_label = QLabel(f"Username: {username}")
            username_label.setFont(QFont("Arial", 14))
            username_label.setStyleSheet("color: #4a5568;")
            layout.addWidget(username_label)
            
            # Current role label
            current_role_label = QLabel(f"Current Role: {current_role}")
            current_role_label.setFont(QFont("Arial", 14))
            current_role_label.setStyleSheet("color: #4a5568;")
            layout.addWidget(current_role_label)
            
            # New role selection
            role_layout = QHBoxLayout()
            role_layout.addWidget(QLabel("New Role:"))
            
            role_combo = QComboBox()
            role_combo.addItems(["Employee", "Director"])
            role_combo.setCurrentText(current_role)
            role_combo.setStyleSheet("""
                QComboBox {
                    background-color: #ed8936;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            role_layout.addWidget(role_combo)
            layout.addLayout(role_layout)
            
            # Buttons
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e2e8f0;
                    color: #2d3748;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #cbd5e1;
                }
            """)
            cancel_btn.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_btn)
            
            update_btn = QPushButton("Update Role")
            update_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ed8936;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #dd6b20;
                }
            """)
            
            def update_role():
                new_role = role_combo.currentText()
                if new_role != current_role:
                    # Update in database
                    try:
                        from app.db import create_connection, update_user_role
                        conn = create_connection()
                        if conn:
                            success = update_user_role(conn, user_id, new_role)
                            conn.close()
                            if success:
                                # Update in table
                                current_role_item.setText(new_role)
                                role_color = "#10b981" if new_role == "Director" else "#6b7280"
                                current_role_item.setForeground(QColor(role_color))
                                QMessageBox.information(self, "Success", "User role updated successfully")
                                dialog.accept()
                            else:
                                QMessageBox.critical(self, "Error", "Failed to update user role")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Error updating role: {str(e)}")
                else:
                    dialog.reject()
            
            update_btn.clicked.connect(update_role)
            button_layout.addWidget(update_btn)
            
            layout.addLayout(button_layout)
            dialog.exec_()
            
        except Exception as e:
            print(f"Error editing user role: {e}")
            QMessageBox.critical(self, "Error", f"Failed to edit user role: {str(e)}")
    
    def delete_user(self, user_id, row):
        """Delete user"""
        try:
            username_item = self.users_table.item(row, 1)
            username = username_item.text() if username_item else "Unknown"
            
            reply = QMessageBox.question(self, "Delete User", 
                                       f"Are you sure you want to delete user '{username}'?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # TODO: Implement delete user in database
                QMessageBox.information(self, "Delete User", "User deletion will be implemented")
                
        except Exception as e:
            print(f"Error deleting user: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")
    
    def load_projects_for_reports(self):
        """Load projects into the combo box for reports"""
        try:
            from app.db import create_connection, read_projets
            conn = create_connection()
            if conn:
                projects = read_projets(conn)
                self.project_combo.clear()
                self.project_combo.addItem("All Projects", None)
                
                for project in projects:
                    project_name = project[1] if len(project) > 1 else "Unknown"
                    project_id = project[0] if len(project) > 0 else None
                    self.project_combo.addItem(project_name, project_id)
                
                conn.close()
        except Exception as e:
            print(f"Error loading projects for reports: {e}")
    
    def select_report_type(self, report_type):
        """Handle report type selection"""
        if report_type == 'invoice':
            self.invoice_report_btn.setChecked(True)
            self.complete_report_btn.setChecked(False)
        elif report_type == 'complete':
            self.invoice_report_btn.setChecked(False)
            self.complete_report_btn.setChecked(True)
    
    def select_date_range(self, button):
        """Handle date range selection"""
        # Uncheck all other date buttons
        for btn in self.date_buttons:
            if btn != button:
                btn.setChecked(False)
        
        button.setChecked(True)
        
        # Show/hide custom date range inputs
        date_value = button.property("date_value")
        if date_value == "custom":
            self.custom_date_container.setVisible(True)
        else:
            self.custom_date_container.setVisible(False)
    
    def generate_pdf_report(self):
        """Generate PDF report based on selected options"""
        try:
            # Get selected options
            selected_project_index = self.project_combo.currentIndex()
            selected_project_id = self.project_combo.itemData(selected_project_index)
            
            # Determine report type
            if self.invoice_report_btn.isChecked():
                report_type = 'invoice'
            elif self.complete_report_btn.isChecked():
                report_type = 'complete'
            else:
                QMessageBox.warning(self, "No Selection", "Please select a report type.")
                return
            
            # Get date range
            selected_date_btn = None
            for btn in self.date_buttons:
                if btn.isChecked():
                    selected_date_btn = btn
                    break
            
            if not selected_date_btn:
                QMessageBox.warning(self, "No Selection", "Please select a date range.")
                return
            
            date_value = selected_date_btn.property("date_value")
            
            # Get custom dates if selected
            custom_start_date = None
            custom_end_date = None
            if date_value == "custom":
                custom_start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
                custom_end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            
            # Validate complete report requires project selection
            if report_type == 'complete' and selected_project_id is None:
                QMessageBox.warning(self, "Project Required", 
                                  "Complete project report requires selecting a specific project.")
                return
            
            # Generate PDF
            from app.pdf_generator import PDFReportGenerator
            
            # Show progress dialog
            from PyQt5.QtWidgets import QProgressDialog
            from PyQt5.QtCore import Qt
            
            progress = QProgressDialog("Generating PDF report...", "Cancel", 0, 0, self)
            progress.setWindowTitle("Generating Report")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.show()
            
            # Process events to show dialog
            QApplication.processEvents()
            
            generator = PDFReportGenerator()
            
            if report_type == 'invoice':
                output_file = generator.generate_invoice_report(
                    project_id=selected_project_id,
                    period=date_value,
                    custom_start_date=custom_start_date,
                    custom_end_date=custom_end_date
                )
            else:  # complete
                output_file = generator.generate_complete_project_report(
                    project_id=selected_project_id,
                    period=date_value,
                    custom_start_date=custom_start_date,
                    custom_end_date=custom_end_date
                )
            
            progress.close()
            
            # Show success message with option to open file
            from PyQt5.QtWidgets import QPushButton
            msg = QMessageBox(self)
            msg.setWindowTitle("Report Generated")
            msg.setText(f"PDF report has been generated successfully!")
            msg.setInformativeText(f"File saved as: {output_file}")
            msg.setIcon(QMessageBox.Information)
            
            # Add custom buttons
            open_btn = msg.addButton("Open PDF", QMessageBox.ActionRole)
            open_folder_btn = msg.addButton("Open Folder", QMessageBox.ActionRole)
            ok_btn = msg.addButton(QMessageBox.Ok)
            
            msg.exec_()
            
            if msg.clickedButton() == open_btn:
                # Open PDF file
                import os
                import subprocess
                if os.name == 'nt':  # Windows
                    os.startfile(output_file)
                else:  # macOS and Linux
                    subprocess.call(['open' if os.name == 'posix' else 'xdg-open', output_file])
            elif msg.clickedButton() == open_folder_btn:
                # Open folder containing the file
                import os
                import subprocess
                folder_path = os.path.dirname(os.path.abspath(output_file))
                if os.name == 'nt':  # Windows
                    subprocess.run(['explorer', folder_path])
                else:  # macOS and Linux
                    subprocess.call(['open' if os.name == 'posix' else 'xdg-open', folder_path])
            
        except Exception as e:
            if 'progress' in locals():
                progress.close()
            QMessageBox.critical(self, "Error", f"Failed to generate PDF report:\n{str(e)}")
            import traceback
            traceback.print_exc()
