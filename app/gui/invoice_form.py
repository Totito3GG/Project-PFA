from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QDateEdit, QDoubleSpinBox, QMessageBox, QGroupBox,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from app.db import create_connection, create_facture_charge, read_projets, create_ligne_charge


class InvoiceDetailsDialog(QDialog):
    """Dialog for viewing invoice details in modern dashboard style"""
    def __init__(self, invoice_data=None, expense_lines=None, parent=None):
        super().__init__(parent)
        self.invoice_data = invoice_data or {}
        self.expense_lines = expense_lines or []
        self.parent_window = parent  # Store parent reference for updating
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Invoice Details")
        self.setModal(True)
        self.setFixedSize(1200, 800)  # Match main window resolution
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)

        # Header with title and buttons
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Invoice Details")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2d3748;
                margin: 0;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #d69e2e;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #b7791f;
            }
        """)
        edit_btn.clicked.connect(self.edit_invoice)
        header_layout.addWidget(edit_btn)
        
        # Mark as Paid button
        mark_paid_btn = QPushButton("Mark as Paid")
        mark_paid_btn.setStyleSheet(edit_btn.styleSheet())
        mark_paid_btn.clicked.connect(self.mark_as_paid)
        header_layout.addWidget(mark_paid_btn)
        
        main_layout.addLayout(header_layout)

        # Invoice info row
        info_frame = QGroupBox()
        info_frame.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                margin: 10px 0;
            }
        """)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setSpacing(60)
        
        # Create info labels
        invoice_num_label = QLabel(f"<b>Invoice Number:</b><br>{self.invoice_data.get('number', 'N/A')}")
        supplier_label = QLabel(f"<b>Supplier Name:</b><br>{self.invoice_data.get('supplier', 'ABC Construction Ltd.')}")
        date_label = QLabel(f"<b>Invoice Date:</b><br>{self.invoice_data.get('date', 'March 15, 2024')}")
        
        # Store reference to amount label for updating
        self.amount_label = QLabel(f"<b>Total Amount:</b><br><span style='color:#d69e2e;font-weight:bold;font-size:16px;'>${self.invoice_data.get('amount', '0.00')}</span>")
        amount_label = self.amount_label
        
        # Status selector section
        status_container = QVBoxLayout()
        status_title = QLabel("<b>Invoice Status:</b>")
        status_title.setStyleSheet("font-size: 14px; color: #2d3748; padding: 0; margin: 0 0 5px 0;")
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Paid", "Pending", "Overdue"])
        
        # Set current status (default to Pending if not specified)
        current_status = self.invoice_data.get('status', 'Pending')
        status_index = self.status_combo.findText(current_status)
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)
        
        self.status_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
                font-weight: bold;
                min-width: 100px;
            }
            QComboBox:hover {
                border-color: #cbd5e0;
            }
            QComboBox:focus {
                border-color: #d69e2e;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        
        # Connect status change to update function
        self.status_combo.currentTextChanged.connect(self.on_status_changed)
        
        status_container.addWidget(status_title)
        status_container.addWidget(self.status_combo)
        status_container.addStretch()
        
        # Create a widget for the status section
        status_widget = QWidget()
        status_widget.setLayout(status_container)
        
        # Style the info labels
        for label in [invoice_num_label, supplier_label, date_label, amount_label]:
            label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #2d3748;
                    padding: 8px 0;
                }
            """)
        
        info_layout.addWidget(invoice_num_label)
        info_layout.addWidget(supplier_label)
        info_layout.addWidget(date_label)
        info_layout.addWidget(amount_label)
        info_layout.addWidget(status_widget)  # Add the status selector
        info_layout.addStretch()
        
        main_layout.addWidget(info_frame)

        # Expense table
        expense_table = QTableWidget()
        expense_table.setColumnCount(4)
        expense_table.setHorizontalHeaderLabels(["Expense Lines", "Unit Price", "Quantity", "Total"])
        expense_table.setMinimumHeight(250)  # Increased height for better visibility
        
        # Start with empty table - user will add expenses manually
        expense_table.setRowCount(0)  # No default expenses
        
        # Make table editable - use simple approach
        try:
            # Enable all edit triggers for easy editing
            from PyQt5.QtWidgets import QAbstractItemView
            expense_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
            print("Edit triggers set successfully")
        except Exception as e:
            print(f"Edit triggers error: {e}")
            # Most basic fallback
            expense_table.setEditTriggers(3)  # AllEditTriggers numeric value
        
        # Connect itemChanged signal to handle calculations
        expense_table.itemChanged.connect(self.on_item_changed)
        
        expense_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                gridline-color: #e2e8f0;
                font-size: 14px;
                selection-background-color: #f7fafc;
            }
            QHeaderView::section {
                background-color: #f7fafc;
                color: #4a5568;
                padding: 16px 12px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: bold;
                font-size: 14px;
                text-align: left;
                min-width: 120px;
            }
            QTableWidget::item {
                padding: 16px 12px;
                border-bottom: 1px solid #f7fafc;
                color: #2d3748;
                font-size: 14px;
            }
            QTableWidget::item:selected {
                background-color: #ebf8ff;
            }
        """)
        
        # Set specific column widths to prevent text cutoff
        try:
            header = expense_table.horizontalHeader()
            if header:
                header.resizeSection(0, 300)  # Expense Lines column wider
                header.resizeSection(1, 120)  # Unit Price
                header.resizeSection(2, 100)  # Quantity
                header.resizeSection(3, 120)  # Total
                header.setStretchLastSection(False)
        except Exception as e:
            print(f"Header resize error: {e}")
            # Fallback: use stretch for last section
            try:
                expense_table.horizontalHeader().setStretchLastSection(True)
            except:
                pass
        
        try:
            expense_table.verticalHeader().setVisible(False)
        except Exception as e:
            print(f"Vertical header error: {e}")
        
        try:
            expense_table.setSelectionBehavior(QTableWidget.SelectRows)
        except Exception as e:
            print(f"Selection behavior error: {e}")
        
        # Store reference to table for later use
        self.expense_table = expense_table
        main_layout.addWidget(expense_table)

        # Add Expense Line button
        add_expense_btn = QPushButton("Add Expense Line")
        add_expense_btn.setStyleSheet("""
            QPushButton {
                background-color: #d69e2e;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #b7791f;
            }
        """)
        add_expense_btn.clicked.connect(self.add_expense_line)
        main_layout.addWidget(add_expense_btn)

        # Summary section
        summary_frame = QGroupBox()
        summary_frame.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                margin: 10px 0;
            }
        """)
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.addStretch()
        
        # Summary labels (will be updated dynamically)
        self.subtotal_label = QLabel("Subtotal: $0.00")
        self.subtotal_label.setStyleSheet("font-size: 14px; color: #4a5568; margin-right: 40px;")
        
        self.tax_label = QLabel("TVA (20%): $0.00")
        self.tax_label.setStyleSheet("font-size: 14px; color: #4a5568; margin-right: 40px;")
        
        self.total_due_btn = QPushButton("Total Due: $0.00")
        self.total_due_btn.setStyleSheet("""
            QPushButton {
                background-color: #d69e2e;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        self.total_due_btn.setEnabled(False)  # Make it non-clickable, just for display
        
        summary_layout.addWidget(self.subtotal_label)
        summary_layout.addWidget(self.tax_label)
        summary_layout.addWidget(self.total_due_btn)
        
        # Connect table changes to update totals
        self.expense_table.itemChanged.connect(self.update_totals)
        
        main_layout.addWidget(summary_frame)
        
        # Save and Close buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Save button
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #38a169;
            }
        """)
        save_btn.clicked.connect(self.save_expense_lines)
        button_layout.addWidget(save_btn)
        
        # Close button  
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #718096;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4a5568;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
        # Load existing expense lines if any
        self.load_expense_lines()
    
    def load_expense_lines(self):
        """Load existing expense lines into the table"""
        if not self.expense_lines:
            return
            
        # Set the number of rows
        self.expense_table.setRowCount(len(self.expense_lines))
        
        # Populate the table
        for row, line in enumerate(self.expense_lines):
            try:
                # Assuming expense line format: (id, invoice_id, motif, prix_unitaire, quantite, montant_ligne)
                motif = line[2] if len(line) > 2 else ''
                prix_unitaire = line[3] if len(line) > 3 else 0.0
                quantite = line[4] if len(line) > 4 else 0.0
                montant_ligne = line[5] if len(line) > 5 else 0.0
                
                # Create table items
                motif_item = QTableWidgetItem(str(motif))
                price_item = QTableWidgetItem(f"${prix_unitaire:.2f}")
                qty_item = QTableWidgetItem(str(quantite))
                total_item = QTableWidgetItem(f"${montant_ligne:.2f}")
                
                # Set items in table
                self.expense_table.setItem(row, 0, motif_item)
                self.expense_table.setItem(row, 1, price_item)
                self.expense_table.setItem(row, 2, qty_item)
                self.expense_table.setItem(row, 3, total_item)
                
            except Exception as e:
                print(f"Error loading expense line {row}: {e}")
                continue
        
        # Update totals after loading
        self.update_totals()
    
    def update_totals(self):
        """Calculate and update the totals based on expense table data"""
        try:
            subtotal = 0.0
            
            # Calculate subtotal from all rows in expense table
            for row in range(self.expense_table.rowCount()):
                total_item = self.expense_table.item(row, 3)  # Total column
                if total_item and total_item.text():
                    # Remove $ sign and commas, then convert to float
                    total_text = total_item.text().replace('$', '').replace(',', '')
                    try:
                        row_total = float(total_text)
                        subtotal += row_total
                    except ValueError:
                        continue
            
            # Calculate TVA (20%)
            tva_rate = 0.20
            tva_amount = subtotal * tva_rate
            
            # Calculate final total
            final_total = subtotal + tva_amount
            
            # Update the labels
            self.subtotal_label.setText(f"Subtotal: {subtotal:,.2f}")
            self.tax_label.setText(f"TVA (20%): {tva_amount:,.2f}")
            self.total_due_btn.setText(f"Total Due: {final_total:,.2f}")
            
            # Update the header amount label as well
            self.amount_label.setText(f"<b>Total Amount:</b><br><span style='color:#d69e2e;font-weight:bold;font-size:16px;'>${final_total:,.2f}</span>")
            
        except Exception as e:
            print(f"Error updating totals: {e}")
    
    def calculate_row_total(self, row):
        """Calculate total for a specific row when unit price or quantity changes"""
        try:
            unit_price_item = self.expense_table.item(row, 1)  # Unit Price column
            quantity_item = self.expense_table.item(row, 2)    # Quantity column
            
            if unit_price_item and quantity_item:
                # Extract unit price value
                unit_price_text = unit_price_item.text().replace('$', '').replace(',', '')
                quantity_text = quantity_item.text()
                
                try:
                    unit_price = float(unit_price_text)
                    quantity = float(quantity_text)
                    total = unit_price * quantity
                    
                    # Temporarily disconnect signal to prevent recursion
                    self.expense_table.itemChanged.disconnect()
                    
                    # Update the total column 
                    total_item = QTableWidgetItem(f"${total:,.2f}")
                    self.expense_table.setItem(row, 3, total_item)
                    
                    # Reconnect the signal
                    self.expense_table.itemChanged.connect(self.on_item_changed)
                    
                    # Update overall totals
                    self.update_totals()
                    
                except ValueError:
                    # Reconnect signal even on error
                    try:
                        self.expense_table.itemChanged.connect(self.on_item_changed)
                    except:
                        pass
                    
        except Exception as e:
            print(f"Error in calculate_row_total: {e}")
            # Make sure to reconnect the signal even if there's an error
            try:
                self.expense_table.itemChanged.connect(self.on_item_changed)
            except:
                pass
                    
        except Exception as e:
            print(f"Error calculating row total: {e}")
    
    def edit_invoice(self):
        """Handle edit button click"""
        print("Edit button clicked!")  # Debug print
        try:
            QMessageBox.information(self, "Edit Invoice", 
                                  f"Edit functionality for Invoice #{self.invoice_data.get('number', 'N/A')}\n\nYou can now double-click any cell in the expense table to edit it.")
        except Exception as e:
            print(f"Error in edit_invoice: {e}")
    
    def mark_as_paid(self):
        """Handle mark as paid button click"""
        print("Mark as paid button clicked!")  # Debug print
        try:
            reply = QMessageBox.question(self, "Mark as Paid", 
                                       f"Mark Invoice #{self.invoice_data.get('number', 'N/A')} as paid?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                QMessageBox.information(self, "Success", "Invoice marked as paid!")
        except Exception as e:
            print(f"Error in mark_as_paid: {e}")
    
    def add_expense_line(self):
        """Handle add expense line button click"""
        print("Add expense line button clicked!")  # Debug print
        try:
            # Temporarily disconnect the signal to prevent recursion
            self.expense_table.itemChanged.disconnect()
            
            # Add a new empty row to the table
            row_count = self.expense_table.rowCount()
            self.expense_table.insertRow(row_count)
            
            # Set default values for new row
            self.expense_table.setItem(row_count, 0, QTableWidgetItem("New Expense Item"))
            self.expense_table.setItem(row_count, 1, QTableWidgetItem("0.00"))
            self.expense_table.setItem(row_count, 2, QTableWidgetItem("1"))
            
            # Set initial total (will be calculated automatically)
            total_item = QTableWidgetItem("$0.00")
            self.expense_table.setItem(row_count, 3, total_item)
            
            # Set row height
            self.expense_table.setRowHeight(row_count, 45)
            
            # Reconnect the signal
            self.expense_table.itemChanged.connect(self.on_item_changed)
            
            # Select the new row and start editing the first column
            self.expense_table.setCurrentCell(row_count, 0)
            self.expense_table.edit(self.expense_table.currentIndex())
            
            # Update totals
            self.update_totals()
            
            QMessageBox.information(self, "New Expense Added", 
                                  "New expense line added! Edit Unit Price and Quantity to auto-calculate total.")
        except Exception as e:
            print(f"Error in add_expense_line: {e}")
            # Make sure to reconnect the signal even if there's an error
            try:
                self.expense_table.itemChanged.connect(self.on_item_changed)
            except:
                pass
            QMessageBox.critical(self, "Error", f"Failed to add expense line: {str(e)}")
    
    def on_item_changed(self, item):
        """Handle when an item in the table is changed"""
        try:
            row = item.row()
            column = item.column()
            
            # Prevent editing the total column (column 3) by ignoring changes
            if column == 3:
                return
            
            # If unit price (column 1) or quantity (column 2) changed, recalculate row total
            if column == 1 or column == 2:
                self.calculate_row_total(row)
                
        except Exception as e:
            print(f"Error in on_item_changed: {e}")
    
    def save_expense_lines(self):
        """Save all expense lines to the database"""
        try:
            if 'id' not in self.invoice_data:
                QMessageBox.warning(self, "Warning", "Cannot save: No invoice ID found")
                return
                
            invoice_id = self.invoice_data['id']
            conn = create_connection()
            if not conn:
                QMessageBox.critical(self, "Error", "Cannot connect to database")
                return
                
            # First, delete all existing expense lines for this invoice
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM LigneCharge WHERE id_facture_charge = ?", (invoice_id,))
                print(f"Deleted existing expense lines for invoice {invoice_id}")
            except Exception as e:
                print(f"Error deleting existing lines: {e}")
            
            # Then save all current expense lines from the table
            saved_count = 0
            for row in range(self.expense_table.rowCount()):
                try:
                    motif_item = self.expense_table.item(row, 0)
                    price_item = self.expense_table.item(row, 1)
                    qty_item = self.expense_table.item(row, 2)
                    total_item = self.expense_table.item(row, 3)
                    
                    if motif_item and price_item and qty_item and total_item:
                        motif = motif_item.text().strip()
                        price_text = price_item.text().replace('$', '').replace(',', '')
                        qty_text = qty_item.text()
                        total_text = total_item.text().replace('$', '').replace(',', '')
                        
                        if motif and price_text and qty_text:
                            try:
                                prix_unitaire = float(price_text)
                                quantite = float(qty_text)
                                montant_ligne = float(total_text)
                                
                                if prix_unitaire > 0 and quantite > 0:
                                    ligne_tuple = (invoice_id, motif, prix_unitaire, quantite, montant_ligne)
                                    ligne_id = create_ligne_charge(conn, ligne_tuple)
                                    if ligne_id:
                                        saved_count += 1
                                        print(f"Saved expense line: {motif} - ${montant_ligne:.2f}")
                            except ValueError as ve:
                                print(f"Value error in row {row}: {ve}")
                                continue
                                
                except Exception as e:
                    print(f"Error saving expense line at row {row}: {e}")
                    continue
            
            # Update the main invoice total in FactureCharge table
            try:
                # Calculate total from current expense table (same logic as update_totals)
                subtotal = 0.0
                for row in range(self.expense_table.rowCount()):
                    total_item = self.expense_table.item(row, 3)  # Total column
                    if total_item and total_item.text():
                        total_text = total_item.text().replace('$', '').replace(',', '')
                        try:
                            row_total = float(total_text)
                            subtotal += row_total
                        except ValueError:
                            continue
                
                # Calculate final total with TVA (20%)
                tva_rate = 0.20
                tva_amount = subtotal * tva_rate
                final_total = subtotal + tva_amount
                
                # Update the FactureCharge table with new total
                cursor = conn.cursor()
                cursor.execute("UPDATE FactureCharge SET montant_total = ? WHERE id_facture_charge = ?", 
                             (final_total, invoice_id))
                conn.commit()
                print(f"Updated invoice {invoice_id} total to ${final_total:.2f}")
                
                # Update the header amount label to reflect the saved amount
                self.amount_label.setText(f"<b>Total Amount:</b><br><span style='color:#d69e2e;font-weight:bold;font-size:16px;'>${final_total:,.2f}</span>")
                
            except Exception as e:
                print(f"Error updating invoice total: {e}")
            
            conn.close()
            
            if saved_count > 0:
                QMessageBox.information(self, "Success", f"Saved {saved_count} expense lines successfully!")
                
                # Refresh parent window if available
                if self.parent_window and hasattr(self.parent_window, 'load_project_invoices'):
                    self.parent_window.load_project_invoices()
                elif self.parent_window and hasattr(self.parent_window, 'load_data'):
                    self.parent_window.load_data()
            else:
                QMessageBox.information(self, "Info", "No expense lines to save.")
                
        except Exception as e:
            print(f"Error saving expense lines: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save expense lines: {str(e)}")
    
    def on_status_changed(self, new_status):
        """Handle status change from the dropdown"""
        try:
            print(f"Status changed to: {new_status}")
            
            # Update the invoice data
            self.invoice_data['status'] = new_status
            
            # If we have an invoice ID and parent window, update the status
            if 'id' in self.invoice_data and self.parent_window:
                invoice_id = self.invoice_data['id']
                if hasattr(self.parent_window, 'update_invoice_status'):
                    self.parent_window.update_invoice_status(invoice_id, new_status)
                    print(f"Updated invoice {invoice_id} status in parent window")
                    return  # Skip showing confirmation if parent was updated
                    
            # Show confirmation message
            QMessageBox.information(self, "Status Updated", 
                                  f"Invoice status changed to: {new_status}")
            
            # Fallback: refresh parent window if it has load_data method
            if self.parent_window and hasattr(self.parent_window, 'load_data'):
                self.parent_window.load_data()
                print("Parent window refreshed")
                
        except Exception as e:
            print(f"Error updating status: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update status: {str(e)}")

def show_invoice_details(invoice_data=None, expense_lines=None, parent=None):
    dialog = InvoiceDetailsDialog(invoice_data, expense_lines, parent)
    dialog.exec_()


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
                # Save expense lines if they exist (only for InvoiceDetailsDialog)
                if hasattr(self, 'expense_table'):
                    print(f"Saving {self.expense_table.rowCount()} expense lines...")
                    for row in range(self.expense_table.rowCount()):
                        try:
                            motif_item = self.expense_table.item(row, 0)
                            price_item = self.expense_table.item(row, 1)
                            qty_item = self.expense_table.item(row, 2)
                            total_item = self.expense_table.item(row, 3)
                            
                            if motif_item and price_item and qty_item and total_item:
                                motif = motif_item.text().strip()
                                # Remove $ and commas from price
                                price_text = price_item.text().replace('$', '').replace(',', '')
                                qty_text = qty_item.text()
                                total_text = total_item.text().replace('$', '').replace(',', '')
                                
                                if motif and price_text and qty_text:
                                    try:
                                        prix_unitaire = float(price_text)
                                        quantite = float(qty_text)
                                        montant_ligne = float(total_text)
                                        
                                        if prix_unitaire > 0 and quantite > 0:
                                            ligne_tuple = (invoice_id, motif, prix_unitaire, quantite, montant_ligne)
                                            ligne_id = create_ligne_charge(conn, ligne_tuple)
                                            if ligne_id:
                                                print(f"Saved expense line: {motif} - ${montant_ligne:.2f}")
                                            else:
                                                print(f"Failed to save expense line: {motif}")
                                    except ValueError as ve:
                                        print(f"Value error in expense line {row}: {ve}")
                                        continue
                        except Exception as e:
                            print(f"Error saving expense line at row {row}: {e}")
                            continue
                
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
    return dialog.exec_() == QDialog.Accepted
