#!/usr/bin/env python3
"""
PDF Report Generation Module
Handles generation of various types of PDF reports for the project management system
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime, timedelta
import os
import sqlite3
from typing import List, Dict, Any, Optional


class PDFReportGenerator:
    """Main class for generating PDF reports"""
    
    def __init__(self, db_path: str = "gestion_projets.db"):
        self.db_path = db_path
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#4a5568'),
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.HexColor('#ed8936'),
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='CustomInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_RIGHT
        ))
    
    def get_project_data(self, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch project data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if project_id:
                cursor.execute("""
                    SELECT id_projet, nom_projet, date_estimation, date_lancement, 
                           budget_max, montant_investi, status
                    FROM Projet 
                    WHERE id_projet = ?
                """, (project_id,))
            else:
                cursor.execute("""
                    SELECT id_projet, nom_projet, date_estimation, date_lancement, 
                           budget_max, montant_investi, status
                    FROM Projet 
                    ORDER BY date_lancement DESC
                """)
            
            projects = []
            for row in cursor.fetchall():
                projects.append({
                    'id': row[0],
                    'name': row[1],
                    'date_estimation': row[2],
                    'date_lancement': row[3],
                    'budget_max': row[4],
                    'montant_investi': row[5],
                    'status': row[6] if len(row) > 6 else 'Active',
                    'remaining_budget': row[4] - row[5]
                })
            
            conn.close()
            return projects
            
        except Exception as e:
            print(f"Error fetching project data: {e}")
            return []
    
    def get_invoice_data(self, project_id: Optional[int] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch invoice data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT fc.id_facture_charge, fc.date_facture, fc.fournisseur, 
                       fc.montant_total, fc.status, p.nom_projet, p.id_projet
                FROM FactureCharge fc
                JOIN Projet p ON fc.id_projet = p.id_projet
            """
            params = []
            conditions = []
            
            if project_id:
                conditions.append("fc.id_projet = ?")
                params.append(project_id)
            
            if start_date:
                conditions.append("fc.date_facture >= ?")
                params.append(start_date)
            
            if end_date:
                conditions.append("fc.date_facture <= ?")
                params.append(end_date)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY fc.date_facture DESC"
            
            cursor.execute(query, params)
            
            invoices = []
            for row in cursor.fetchall():
                invoices.append({
                    'id': row[0],
                    'date': row[1],
                    'supplier': row[2],
                    'amount': row[3],
                    'status': row[4],
                    'project_name': row[5],
                    'project_id': row[6]
                })
            
            conn.close()
            return invoices
            
        except Exception as e:
            print(f"Error fetching invoice data: {e}")
            return []
    
    def add_header_with_logo(self, story):
        """Add header with logo and company information"""
        try:
            # Check if logo exists
            logo_path = "Images/LogoX.png"
            if not os.path.exists(logo_path):
                # Try alternative path
                logo_path = os.path.join(os.path.dirname(__file__), "..", "Images", "LogoX.png")
            
            if os.path.exists(logo_path):
                # Create header table with logo and company info
                header_data = []
                
                # Logo (left side)
                logo_img = Image(logo_path, width=120, height=80)  # Large logo as requested
                
                # Company info (right side)
                company_info = Paragraph("""
                    <b>Système de Gestion de Projets & Charges</b><br/>
                    <font size="10">Project Management System</font><br/>
                    <font size="9" color="#6b7280">Professional Report Generation</font>
                """, self.styles['Normal'])
                
                header_data.append([logo_img, company_info])
                
                # Create header table
                header_table = Table(header_data, colWidths=[140, 400])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),   # Logo left aligned
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Company info right aligned
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ]))
                
                story.append(header_table)
                story.append(Spacer(1, 10))
                story.append(HRFlowable(width="100%", thickness=2, lineCap='round', color=colors.HexColor('#ed8936')))
                story.append(Spacer(1, 20))
                
            else:
                # Fallback: text-only header if logo not found
                story.append(Paragraph("Système de Gestion de Projets & Charges", self.styles['CustomTitle']))
                story.append(Spacer(1, 10))
                story.append(HRFlowable(width="100%", thickness=2, lineCap='round', color=colors.HexColor('#ed8936')))
                story.append(Spacer(1, 20))
                
        except Exception as e:
            print(f"Error adding header with logo: {e}")
            # Fallback to simple text header
            story.append(Paragraph("Système de Gestion de Projets & Charges", self.styles['CustomTitle']))
            story.append(Spacer(1, 10))
            story.append(HRFlowable(width="100%", thickness=2, lineCap='round', color=colors.HexColor('#ed8936')))
            story.append(Spacer(1, 20))
    
    def get_date_range(self, period: str) -> tuple[Optional[str], Optional[str]]:
        """Get start and end dates for specified period"""
        today = datetime.now()
        
        if period == "today":
            return today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        elif period == "this_week":
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')
        elif period == "this_month":
            start_of_month = today.replace(day=1)
            if today.month == 12:
                end_of_month = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
            else:
                end_of_month = today.replace(month=today.month+1, day=1) - timedelta(days=1)
            return start_of_month.strftime('%Y-%m-%d'), end_of_month.strftime('%Y-%m-%d')
        else:
            return None, None
    
    def generate_invoice_report(self, project_id: Optional[int], period: str, custom_start_date: Optional[str] = None, custom_end_date: Optional[str] = None, output_file: Optional[str] = None) -> str:
        """Generate invoice-only PDF report"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"invoice_report_{timestamp}.pdf"
        
        # Get date range
        if custom_start_date and custom_end_date:
            start_date, end_date = custom_start_date, custom_end_date
        else:
            start_date, end_date = self.get_date_range(period)
        
        # Get data
        invoices = self.get_invoice_data(project_id, start_date, end_date)
        projects = self.get_project_data(project_id) if project_id else []
        
        # Create PDF
        doc = SimpleDocTemplate(output_file, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        story = []
        
        # Add header with logo
        self.add_header_with_logo(story)
        
        # Report title
        story.append(Paragraph("Invoice Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Report info
        report_info = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        if start_date and end_date:
            report_info += f"<br/>Period: {start_date} to {end_date}"
        if project_id and projects:
            report_info += f"<br/>Project: {projects[0]['name']}"
        
        story.append(Paragraph(report_info, self.styles['CustomInfo']))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.HexColor('#e2e8f0')))
        story.append(Spacer(1, 20))
        
        if not invoices:
            story.append(Paragraph("No invoices found for the specified criteria.", self.styles['Normal']))
        else:
            # Summary
            total_amount = sum(inv['amount'] for inv in invoices)
            story.append(Paragraph(f"Summary", self.styles['CustomHeader']))
            story.append(Paragraph(f"Total Invoices: {len(invoices)}", self.styles['Normal']))
            story.append(Paragraph(f"Total Amount: {total_amount:,.2f} DH", self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Invoice table
            story.append(Paragraph("Invoice Details", self.styles['CustomHeader']))
            
            # Table data
            table_data = [['Invoice ID', 'Date', 'Supplier', 'Amount (DH)', 'Status', 'Project']]
            
            for inv in invoices:
                table_data.append([
                    f"INV-{inv['id']:03d}",
                    inv['date'],
                    inv['supplier'],
                    f"{inv['amount']:,.2f}",
                    inv['status'],
                    inv['project_name']
                ])
            
            # Create table
            table = Table(table_data, colWidths=[80, 80, 120, 80, 60, 120])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ed8936')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),  # Amount column right-aligned
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
            ]))
            
            story.append(table)
        
        # Build PDF
        doc.build(story)
        return output_file
    
    def generate_complete_project_report(self, project_id: int, period: str, custom_start_date: Optional[str] = None, custom_end_date: Optional[str] = None, output_file: Optional[str] = None) -> str:
        """Generate complete project PDF report with project details and invoices"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"project_report_{timestamp}.pdf"
        
        # Get date range
        if custom_start_date and custom_end_date:
            start_date, end_date = custom_start_date, custom_end_date
        else:
            start_date, end_date = self.get_date_range(period)
        
        # Get data
        projects = self.get_project_data(project_id)
        if not projects:
            raise ValueError(f"Project with ID {project_id} not found")
        
        project = projects[0]
        invoices = self.get_invoice_data(project_id, start_date, end_date)
        
        # Create PDF
        doc = SimpleDocTemplate(output_file, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        story = []
        
        # Add header with logo
        self.add_header_with_logo(story)
        
        # Report title
        story.append(Paragraph("Complete Project Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Report info
        report_info = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        if start_date and end_date:
            report_info += f"<br/>Period: {start_date} to {end_date}"
        
        story.append(Paragraph(report_info, self.styles['CustomInfo']))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.HexColor('#e2e8f0')))
        story.append(Spacer(1, 20))
        
        # Project Information
        story.append(Paragraph("Project Information", self.styles['CustomHeader']))
        
        project_info = [
            ['Project Name:', project['name']],
            ['Status:', project['status']],
            ['Date de fin du projet:', project['date_estimation'] if project['date_estimation'] else 'N/A'],
            ['Launch Date:', project['date_lancement'] if project['date_lancement'] else 'N/A'],
            ['Total Budget:', f"{project['budget_max']:,.2f} DH"],
            ['Amount Invested:', f"{project['montant_investi']:,.2f} DH"],
            ['Remaining Budget:', f"{project['remaining_budget']:,.2f} DH"],
            ['Budget Usage:', f"{(project['montant_investi']/project['budget_max']*100) if project['budget_max'] > 0 else 0:.1f}%"]
        ]
        
        project_table = Table(project_info, colWidths=[150, 300])
        project_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(project_table)
        story.append(Spacer(1, 30))
        
        # Financial Summary
        story.append(Paragraph("Financial Summary", self.styles['CustomHeader']))
        
        total_invoices = len(invoices)
        total_amount = sum(inv['amount'] for inv in invoices)
        avg_invoice = total_amount / total_invoices if total_invoices > 0 else 0
        
        financial_info = [
            ['Total Invoices (Period):', str(total_invoices)],
            ['Total Amount (Period):', f"{total_amount:,.2f} DH"],
            ['Average Invoice Amount:', f"{avg_invoice:,.2f} DH"],
            ['Budget Utilization:', f"{(project['montant_investi']/project['budget_max']*100) if project['budget_max'] > 0 else 0:.1f}%"]
        ]
        
        financial_table = Table(financial_info, colWidths=[150, 300])
        financial_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(financial_table)
        story.append(Spacer(1, 30))
        
        # Invoice Details
        if invoices:
            story.append(Paragraph("Invoice Details", self.styles['CustomHeader']))
            
            # Table data
            table_data = [['Invoice ID', 'Date', 'Supplier', 'Amount (DH)', 'Status']]
            
            for inv in invoices:
                table_data.append([
                    f"INV-{inv['id']:03d}",
                    inv['date'],
                    inv['supplier'],
                    f"{inv['amount']:,.2f}",
                    inv['status']
                ])
            
            # Create table
            table = Table(table_data, colWidths=[80, 80, 150, 100, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ed8936')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),  # Amount column right-aligned
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
            ]))
            
            story.append(table)
        else:
            story.append(Paragraph("No invoices found for the specified period.", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return output_file
