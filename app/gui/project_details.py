from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QWidget,
    QMessageBox, QComboBox, QGroupBox, QTabWidget, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from app.db import create_connection, read_lignes_charge_by_facture
from app.utils import format_currency, format_date


class ProjectDetailsDialog(QDialog):
    """Dialog for viewing and managing project details with invoices"""
    
    def __init__(self, project_data=None, parent=None, user_role="Employe"):
        super().__init__(parent)
        self.project_data = project_data
        self.parent_window = parent
        self.user_role = user_role  # Store user role for access control
        self.invoice_ids = []
        self.project_statuses = {
            'Active': '#10b981',      # Green
            'In Progress': '#f59e0b', # Orange
            'Completed': '#6b7280'    # Gray
        }
        
        self.setup_ui()
        self.load_project_invoices()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(f"Project Details: {self.project_data.get('nom_projet', 'Unknown Project')}")
        self.setModal(True)
        self.resize(1200, 800)
        
        # Apply modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2d3748;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #2d3748;
                font-size: 13px;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Header with project info and actions
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # Project info section - smaller space
        info_section = self.create_project_info_section()
        main_layout.addWidget(info_section, 1)  # Give it weight of 1
        
        # Tabs for different sections - larger space
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #f7fafc;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #ed8936;
            }
        """)
        
        # Invoices tab
        invoices_tab = self.create_invoices_tab()
        tabs.addTab(invoices_tab, "Invoices")
        
        # Expenses tab (placeholder for now)
        expenses_tab = QWidget()
        tabs.addTab(expenses_tab, "Expenses")
        
        # Reports tab (placeholder for now)
        reports_tab = QWidget()
        tabs.addTab(reports_tab, "Reports")
        
        main_layout.addWidget(tabs, 3)  # Give it weight of 3 (3 times more space than project info)
        
        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        
        main_layout.addLayout(close_layout)
    
    def create_header(self):
        """Create header with title and action buttons"""
        header_layout = QHBoxLayout()
        
        # Project title
        title_label = QLabel(f"Project Details")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: #2d3748;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Only show Edit and Archive buttons for Directors
        if self.user_role == "Directeur":
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
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
            edit_btn.clicked.connect(self.edit_project)
            header_layout.addWidget(edit_btn)
            
            # Archive button
            archive_btn = QPushButton("Archive Project")
            archive_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            header_layout.addWidget(archive_btn)
        else:
            # Show read-only indicator for Employees
            readonly_label = QLabel("Read Only Access")
            readonly_label.setStyleSheet("""
                QLabel {
                    color: #6b7280;
                    font-style: italic;
                    font-size: 14px;
                    padding: 10px 20px;
                    background-color: #f7fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                }
            """)
            header_layout.addWidget(readonly_label)
        
        return header_layout
    
    def create_project_info_section(self):
        """Create project information section matching the exact design"""
        info_group = QGroupBox("Project Information")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #2d3748;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """)
        info_layout = QVBoxLayout(info_group)
        info_layout.setSpacing(15)  # Reduced from 25
        
        # Project Name - Large but more compact
        project_name = self.project_data.get('nom_projet', 'N/A')
        project_name_label = QLabel(project_name)
        project_name_label.setFont(QFont("Arial", 32, QFont.Bold))  # Reduced from 40
        project_name_label.setStyleSheet("color: #2d3748; margin: 5px 0 15px 0;")  # Reduced margins
        project_name_label.setAlignment(Qt.AlignLeft)
        info_layout.addWidget(project_name_label)
        
        # Create the grid layout exactly like your design
        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setSpacing(30)  # Reduced from 50
        
        # Get values
        budget_max = self.project_data.get('budget_max', 0)
        montant_investi = self.project_data.get('montant_investi', 0)
        remaining = budget_max - montant_investi
        
        # Left Column
        left_column = QVBoxLayout()
        left_column.setSpacing(12)  # Reduced from 20
        
        # Total Budget
        total_budget_label = QLabel("Total Budget:")
        total_budget_label.setFont(QFont("Arial", 14))
        total_budget_label.setStyleSheet("color: #718096; margin-bottom: 5px;")
        left_column.addWidget(total_budget_label)
        
        total_budget_value = QLabel(format_currency(budget_max))
        total_budget_value.setFont(QFont("Arial", 18, QFont.Bold))
        total_budget_value.setStyleSheet("color: #2d3748; margin-bottom: 15px;")
        left_column.addWidget(total_budget_value)
        
        # Remaining Budget
        remaining_label = QLabel("Remaining:")
        remaining_label.setFont(QFont("Arial", 14))
        remaining_label.setStyleSheet("color: #718096; margin-bottom: 5px;")
        left_column.addWidget(remaining_label)
        
        remaining_value = QLabel(format_currency(remaining))
        remaining_value.setFont(QFont("Arial", 18, QFont.Bold))
        remaining_value.setStyleSheet("color: #2d3748;")
        left_column.addWidget(remaining_value)
        
        grid_layout.addLayout(left_column)
        
        # Middle Column  
        middle_column = QVBoxLayout()
        middle_column.setSpacing(12)  # Reduced from 20
        
        # Spent Amount
        spent_label = QLabel("Spent Amount:")
        spent_label.setFont(QFont("Arial", 14))
        spent_label.setStyleSheet("color: #718096; margin-bottom: 5px;")
        middle_column.addWidget(spent_label)
        
        spent_value = QLabel(format_currency(montant_investi))
        spent_value.setFont(QFont("Arial", 18, QFont.Bold))
        spent_value.setStyleSheet("color: #2d3748; margin-bottom: 15px;")
        middle_column.addWidget(spent_value)
        
        # Start Date  
        start_date_label = QLabel("Start Date:")
        start_date_label.setFont(QFont("Arial", 14))
        start_date_label.setStyleSheet("color: #718096; margin-bottom: 5px;")
        middle_column.addWidget(start_date_label)
        
        start_date_value = QLabel(format_date(self.project_data.get('date_lancement', '')))
        start_date_value.setFont(QFont("Arial", 18, QFont.Bold))
        start_date_value.setStyleSheet("color: #2d3748;")
        middle_column.addWidget(start_date_value)
        
        grid_layout.addLayout(middle_column)
        
        # Right Column
        right_column = QVBoxLayout()
        right_column.setSpacing(12)  # Reduced from 20
        
        # Amount (same as budget for display)
        amount_label = QLabel("Amount:")
        amount_label.setFont(QFont("Arial", 14))
        amount_label.setStyleSheet("color: #718096; margin-bottom: 5px;")
        right_column.addWidget(amount_label)
        
        amount_value = QLabel(format_currency(budget_max))
        amount_value.setFont(QFont("Arial", 18, QFont.Bold))
        amount_value.setStyleSheet("color: #2d3748; margin-bottom: 15px;")
        right_column.addWidget(amount_value)
        
        # Status with dropdown - use database status
        status_label = QLabel("Status:")
        status_label.setFont(QFont("Arial", 14))
        status_label.setStyleSheet("color: #718096; margin-bottom: 5px;")
        right_column.addWidget(status_label)
        
        # Use status from database instead of calculating
        current_status = self.project_data.get('status', 'Active')
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(['Active', 'In Progress', 'Completed'])
        self.status_combo.setCurrentText(current_status)
        self.status_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 16px;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
                background-color: #10b981;
                color: white;
                min-width: 100px;
                max-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        self.status_combo.currentTextChanged.connect(self.on_status_changed)
        right_column.addWidget(self.status_combo)
        right_column.addStretch()
        
        grid_layout.addLayout(right_column)
        
        # Add some stretch to right
        grid_layout.addStretch()
        
        info_layout.addWidget(grid_widget)
        
        # Add estimated date at the bottom right
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        estimated_section = QVBoxLayout()
        estimated_label = QLabel("Estimated Date:")
        estimated_label.setFont(QFont("Arial", 14))
        estimated_label.setStyleSheet("color: #718096; margin-bottom: 5px;")
        estimated_section.addWidget(estimated_label)
        
        estimated_value = QLabel(format_date(self.project_data.get('date_estimation', '')))
        estimated_value.setFont(QFont("Arial", 18, QFont.Bold))
        estimated_value.setStyleSheet("color: #2d3748;")
        estimated_section.addWidget(estimated_value)
        
        bottom_layout.addLayout(estimated_section)
        info_layout.addLayout(bottom_layout)
        
        return info_group
    
    def create_invoices_tab(self):
        """Create invoices tab with table and actions"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        
        # Header with Add Invoice button (Director only)
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Invoices"))
        header_layout.addStretch()
        
        if self.user_role == "Directeur":
            add_invoice_btn = QPushButton("Add Invoice")
            add_invoice_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ed8936;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #dd6b20;
                }
            """)
            add_invoice_btn.clicked.connect(self.add_invoice)
            header_layout.addWidget(add_invoice_btn)
        
        layout.addLayout(header_layout)
        
        # Invoices table
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(6)  # Back to 6 columns for Edit and Delete buttons
        self.invoices_table.setHorizontalHeaderLabels([
            "Invoice ID", "Supplier", "Date", "Status", "Total Amount", "Actions"
        ])
        
        # Table styling to match your design
        self.invoices_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
                gridline-color: #f0f0f0;
                selection-background-color: #f8fafc;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 20px 15px;
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
                padding: 20px 15px;
                text-align: left;
            }
        """)
        
        self.invoices_table.setAlternatingRowColors(False)
        self.invoices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.invoices_table.verticalHeader().setVisible(False)
        self.invoices_table.setShowGrid(False)
        self.invoices_table.setRowHeight(0, 80)  # Set default row height
        
        layout.addWidget(self.invoices_table)
        
        return tab_widget
    
    def load_project_invoices(self):
        """Load invoices for the current project"""
        try:
            conn = create_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_facture_charge, date_facture, fournisseur, montant_total, status
                FROM FactureCharge 
                WHERE id_projet = ?
                ORDER BY date_facture DESC
            """, (self.project_data.get('id_projet'),))
            
            invoices = cursor.fetchall()
            conn.close()
            
            self.display_invoices_table(invoices)
            
        except Exception as e:
            print(f"Error loading project invoices: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load project invoices: {str(e)}")
    
    def display_invoices_table(self, invoices):
        """Display invoices in the table with status badges and action buttons"""
        if not invoices:
            self.invoices_table.setRowCount(0)
            return
        
        self.invoices_table.setRowCount(len(invoices))
        self.invoice_ids = []
        
        for row, invoice_tuple in enumerate(invoices):
            self.invoice_ids.append(invoice_tuple[0])
            invoice_id = f"INV-{invoice_tuple[0]:03d}"
            supplier = invoice_tuple[2] if invoice_tuple[2] else 'N/A'
            date_str = format_date(invoice_tuple[1])
            amount = invoice_tuple[3] if invoice_tuple[3] else 0
            # Get status from database (index 4) or default to 'Pending'
            status = invoice_tuple[4] if len(invoice_tuple) > 4 and invoice_tuple[4] else 'Pending'
            
            # Invoice ID - Bold and prominent
            item_id = QTableWidgetItem(invoice_id)
            item_id.setFont(QFont("Arial", 14, QFont.Bold))
            item_id.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.invoices_table.setItem(row, 0, item_id)
            
            # Supplier
            item_supplier = QTableWidgetItem(supplier)
            item_supplier.setFont(QFont("Arial", 14))
            item_supplier.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.invoices_table.setItem(row, 1, item_supplier)
            
            # Date
            item_date = QTableWidgetItem(date_str)
            item_date.setFont(QFont("Arial", 14))
            item_date.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
            self.invoices_table.setItem(row, 2, item_date)
            
            # Status - Create colored status badge using database status
            status_widget = self.create_status_widget(status)
            self.invoices_table.setCellWidget(row, 3, status_widget)
            
            # Amount - Right aligned and bold
            item_amount = QTableWidgetItem(format_currency(amount))
            item_amount.setFont(QFont("Arial", 14, QFont.Bold))
            item_amount.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.invoices_table.setItem(row, 4, item_amount)
            
            # Actions - Only Delete button now
            actions_widget = self.create_actions_widget(row)
            self.invoices_table.setCellWidget(row, 5, actions_widget)
            
            # Set row height for better appearance
            self.invoices_table.setRowHeight(row, 80)
        
        # Configure column widths to match your design
        header = self.invoices_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Invoice ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Supplier
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Date  
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Amount
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Actions
    
    def get_invoice_status(self, invoice_id):
        """Get invoice status from parent window or return default"""
        if self.parent_window and hasattr(self.parent_window, 'invoice_statuses'):
            return self.parent_window.invoice_statuses.get(invoice_id, 'Pending')
        return 'Pending'
    
    def create_status_widget(self, status):
        """Create a colored status widget matching the design"""
        # Updated status colors to match your design
        status_colors = {
            'Paid': '#10b981',     # Green - matching your Paid status
            'Pending': '#f59e0b',  # Orange - matching your Pending status  
            'Overdue': '#ef4444',  # Red - matching your Overdue status
            'Tald': '#f59e0b',     # Orange for Tald status as shown
            'Betto': '#f59e0b'     # Orange for Betto status as shown
        }
        
        bg_color = status_colors.get(status, '#6b7280')
        
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setAlignment(Qt.AlignCenter)
        
        label = QLabel(status)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
                min-width: 70px;
            }}
        """)
        
        layout.addWidget(label)
        return widget
    
    def create_actions_widget(self, row):
        """Create action buttons widget with Delete only (Director only)"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)
        
        # Only show Delete button for Directors
        if self.user_role == "Directeur":
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 60px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            delete_btn.clicked.connect(lambda: self.delete_invoice(row))
            layout.addWidget(delete_btn)
        else:
            # Show read-only label for Employees
            readonly_label = QLabel("Read Only")
            readonly_label.setStyleSheet("""
                QLabel {
                    color: #6b7280;
                    font-style: italic;
                    font-size: 11px;
                    padding: 8px;
                }
            """)
            layout.addWidget(readonly_label)
        
        return widget
    
    def on_status_changed(self, new_status):
        """Handle project status change"""
        try:
            print(f"Project status changed to: {new_status}")
            
            # Update project status in parent window if available
            if self.parent_window and hasattr(self.parent_window, 'update_project_status'):
                project_id = self.project_data.get('id_projet')
                self.parent_window.update_project_status(project_id, new_status)
                print(f"Updated project {project_id} status in parent window")
            else:
                QMessageBox.information(self, "Status Updated", 
                                      f"Project status changed to: {new_status}")
                
        except Exception as e:
            print(f"Error updating project status: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update status: {str(e)}")
    
    def edit_project(self):
        """Edit only the project budget information in header box"""
        # Check if user has permission
        if self.user_role != "Directeur":
            QMessageBox.warning(self, "Access Denied", "Only Directors can edit project details.")
            return
            
        try:
            # Create a simple budget edit dialog
            from PyQt5.QtWidgets import QDialog, QFormLayout, QDoubleSpinBox, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Project Budget")
            dialog.setModal(True)
            dialog.setFixedSize(400, 250)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #f8fafc;
                }
                QLabel {
                    color: #2d3748;
                    font-size: 14px;
                    font-weight: bold;
                }
                QDoubleSpinBox {
                    padding: 8px;
                    border: 2px solid #e2e8f0;
                    border-radius: 6px;
                    font-size: 14px;
                }
            """)
            
            layout = QFormLayout(dialog)
            layout.setSpacing(20)
            
            # Current values
            current_budget = self.project_data.get('budget_max', 0)
            current_invested = self.project_data.get('montant_investi', 0)
            
            # Budget input
            budget_spin = QDoubleSpinBox()
            budget_spin.setRange(0, 999999999.99)
            budget_spin.setDecimals(2)
            budget_spin.setSuffix(" DH")
            budget_spin.setValue(current_budget)
            layout.addRow("Total Budget:", budget_spin)
            
            # Invested amount (read-only display)
            invested_label = QLabel(f"{current_invested:,.2f} DH")
            invested_label.setStyleSheet("color: #718096; background-color: #f0f0f0; padding: 8px; border-radius: 6px;")
            layout.addRow("Amount Invested:", invested_label)
            
            # Remaining (calculated display)
            remaining_label = QLabel(f"{current_budget - current_invested:,.2f} DH")
            remaining_label.setStyleSheet("color: #718096; background-color: #f0f0f0; padding: 8px; border-radius: 6px;")
            layout.addRow("Remaining Budget:", remaining_label)
            
            # Update remaining when budget changes
            def update_remaining():
                new_budget = budget_spin.value()
                new_remaining = new_budget - current_invested
                remaining_label.setText(f"{new_remaining:,.2f} DH")
                
            budget_spin.valueChanged.connect(update_remaining)
            
            # Dialog buttons
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.setStyleSheet("""
                QPushButton {
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton[text="OK"] {
                    background-color: #10b981;
                    color: white;
                }
                QPushButton[text="OK"]:hover {
                    background-color: #059669;
                }
                QPushButton[text="Cancel"] {
                    background-color: #6b7280;
                    color: white;
                }
                QPushButton[text="Cancel"]:hover {
                    background-color: #4b5563;
                }
            """)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addRow(button_box)
            
            if dialog.exec_() == QDialog.Accepted:
                new_budget = budget_spin.value()
                
                # Update the project in database
                conn = create_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE Projet 
                        SET budget_max = ?
                        WHERE id_projet = ?
                    """, (new_budget, self.project_data.get('id_projet')))
                    conn.commit()
                    conn.close()
                    
                    # Update local data
                    self.project_data['budget_max'] = new_budget
                    
                    # Refresh the dialog
                    QMessageBox.information(self, "Success", "Project budget updated successfully!")
                    
                    # Refresh parent window and close this dialog
                    if self.parent_window and hasattr(self.parent_window, 'load_data'):
                        self.parent_window.load_data()
                    
                    # Recreate the project info section with new data
                    self.setup_ui()
                    
        except Exception as e:
            print(f"Error editing project budget: {e}")
            QMessageBox.critical(self, "Error", f"Failed to edit project budget: {str(e)}")
    
    def add_invoice(self):
        """Add a new invoice to this project"""
        try:
            from app.gui.invoice_form import show_invoice_form
            
            if show_invoice_form(self):
                # Refresh the invoices table
                self.load_project_invoices()
                # Refresh parent window if available
                if self.parent_window and hasattr(self.parent_window, 'load_data'):
                    self.parent_window.load_data()
                    
        except Exception as e:
            print(f"Error adding invoice: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add invoice: {str(e)}")
    
    def edit_invoice(self, row):
        """Edit the selected invoice"""
        try:
            if row < len(self.invoice_ids):
                invoice_id = self.invoice_ids[row]
                
                # Get invoice data
                invoice_data = {
                    'id': invoice_id,
                    'number': self.invoices_table.item(row, 0).text() if self.invoices_table.item(row, 0) else '',
                    'supplier': self.invoices_table.item(row, 1).text() if self.invoices_table.item(row, 1) else '',
                    'date': self.invoices_table.item(row, 2).text() if self.invoices_table.item(row, 2) else '',
                    'status': self.get_invoice_status(invoice_id)
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
                
                # Open invoice details dialog with expense lines
                from app.gui.invoice_form import show_invoice_details
                show_invoice_details(invoice_data, expense_lines, self)
                
                # Refresh the table
                self.load_project_invoices()
                
        except Exception as e:
            print(f"Error editing invoice: {e}")
            QMessageBox.critical(self, "Error", f"Failed to edit invoice: {str(e)}")
    
    def delete_invoice(self, row):
        """Delete the selected invoice"""
        # Check if user has permission
        if self.user_role != "Directeur":
            QMessageBox.warning(self, "Access Denied", "Only Directors can delete invoices.")
            return
            
        try:
            if row < len(self.invoice_ids):
                invoice_id = self.invoice_ids[row]
                
                reply = QMessageBox.question(self, "Delete Invoice", 
                                           "Are you sure you want to delete this invoice?",
                                           QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    conn = create_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM FactureCharge WHERE id_facture_charge = ?", (invoice_id,))
                        conn.commit()
                        conn.close()
                        
                        QMessageBox.information(self, "Success", "Invoice deleted successfully")
                        
                        # Refresh the table
                        self.load_project_invoices()
                        # Refresh parent window if available
                        if self.parent_window and hasattr(self.parent_window, 'load_data'):
                            self.parent_window.load_data()
                            
        except Exception as e:
            print(f"Error deleting invoice: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete invoice: {str(e)}")


def show_project_details(project_data=None, parent=None, user_role="Employe"):
    """Show project details dialog"""
    dialog = ProjectDetailsDialog(project_data, parent, user_role)
    dialog.exec_()
