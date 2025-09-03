from fpdf import FPDF
from datetime import datetime
from typing import List, Dict, Optional
import os


class ProjectPDFGenerator:
    """PDF generator for project reports and invoices"""
    
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
    
    def generate_invoice_pdf(self, invoice_data: Dict, lines_data: List[Dict], 
                           project_name: str, output_path: str = None) -> str:
        """Generate PDF for a specific invoice"""
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"facture_{invoice_data.get('id_facture_charge', 'unknown')}_{timestamp}.pdf"
        
        self.pdf = FPDF()
        self.pdf.add_page()
        
        # Header
        self._add_header(project_name)
        
        # Invoice details
        self._add_invoice_details(invoice_data)
        
        # Lines table
        self._add_lines_table(lines_data)
        
        # Footer
        self._add_footer()
        
        # Save PDF
        self.pdf.output(output_path)
        return output_path
    
    def generate_project_report_pdf(self, project_data: Dict, invoices_data: List[Dict], 
                                  output_path: str = None) -> str:
        """Generate comprehensive project report PDF"""
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = project_data.get('nom_projet', 'projet').replace(' ', '_')
            output_path = f"rapport_{safe_name}_{timestamp}.pdf"
        
        self.pdf = FPDF()
        self.pdf.add_page()
        
        # Header
        self._add_header("Rapport de Projet")
        
        # Project summary
        self._add_project_summary(project_data)
        
        # Invoices summary
        if invoices_data:
            self._add_invoices_summary(invoices_data)
        
        # Footer
        self._add_footer()
        
        # Save PDF
        self.pdf.output(output_path)
        return output_path
    
    def _add_header(self, title: str):
        """Add header to PDF"""
        # Title
        self.pdf.set_font('Arial', 'B', 20)
        self.pdf.cell(0, 15, title, 0, 1, 'C')
        
        # Date
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 8, f"Généré le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 0, 1, 'C')
        
        # Line separator
        self.pdf.ln(5)
        self.pdf.set_line_width(0.5)
        self.pdf.line(20, self.pdf.get_y(), 190, self.pdf.get_y())
        self.pdf.ln(10)
    
    def _add_invoice_details(self, invoice_data: Dict):
        """Add invoice details section"""
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 8, "Détails de la Facture", 0, 1, 'L')
        self.pdf.ln(3)
        
        # Invoice info
        self.pdf.set_font('Arial', '', 10)
        
        details = [
            ("Numéro Facture:", str(invoice_data.get('id_facture_charge', 'N/A'))),
            ("Date:", self._format_date(invoice_data.get('date_facture', ''))),
            ("Fournisseur:", invoice_data.get('fournisseur', 'N/A')),
            ("Montant Total:", f"{invoice_data.get('montant_total', 0):,.2f} DH")
        ]
        
        for label, value in details:
            self.pdf.cell(50, 6, label, 0, 0, 'L')
            self.pdf.cell(0, 6, value, 0, 1, 'L')
        
        self.pdf.ln(8)
    
    def _add_project_summary(self, project_data: Dict):
        """Add project summary section"""
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 8, "Résumé du Projet", 0, 1, 'L')
        self.pdf.ln(3)
        
        self.pdf.set_font('Arial', '', 10)
        
        # Calculate remaining budget
        budget_max = project_data.get('budget_max', 0)
        montant_investi = project_data.get('montant_investi', 0)
        reste_budget = budget_max - montant_investi
        pourcentage = (montant_investi / budget_max * 100) if budget_max > 0 else 0
        
        summary = [
            ("Nom du Projet:", project_data.get('nom_projet', 'N/A')),
            ("Date d'Estimation:", self._format_date(project_data.get('date_estimation', ''))),
            ("Date de Lancement:", self._format_date(project_data.get('date_lancement', ''))),
            ("Budget Maximum:", f"{budget_max:,.2f} DH"),
            ("Montant Investi:", f"{montant_investi:,.2f} DH"),
            ("Reste Budget:", f"{reste_budget:,.2f} DH"),
            ("Pourcentage Utilisé:", f"{pourcentage:.1f}%")
        ]
        
        for label, value in summary:
            self.pdf.cell(50, 6, label, 0, 0, 'L')
            self.pdf.cell(0, 6, value, 0, 1, 'L')
        
        # Budget status
        self.pdf.ln(3)
        if reste_budget < 0:
            self.pdf.set_text_color(220, 38, 38)  # Red
            self.pdf.cell(0, 6, "⚠️ PROJET EN DÉPASSEMENT DE BUDGET", 0, 1, 'L')
        elif pourcentage > 80:
            self.pdf.set_text_color(234, 88, 12)  # Orange
            self.pdf.cell(0, 6, "⚠️ ATTENTION: Budget presque épuisé", 0, 1, 'L')
        else:
            self.pdf.set_text_color(22, 163, 74)  # Green
            self.pdf.cell(0, 6, "✅ Budget dans les limites", 0, 1, 'L')
        
        self.pdf.set_text_color(0, 0, 0)  # Reset to black
        self.pdf.ln(8)
    
    def _add_lines_table(self, lines_data: List[Dict]):
        """Add lines table to PDF"""
        if not lines_data:
            return
        
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 8, "Détail des Lignes de Charge", 0, 1, 'L')
        self.pdf.ln(3)
        
        # Table header
        self.pdf.set_font('Arial', 'B', 9)
        self.pdf.set_fill_color(240, 240, 240)
        
        headers = ["Motif", "Prix Unitaire", "Quantité", "Total"]
        widths = [80, 35, 25, 35]
        
        for i, header in enumerate(headers):
            self.pdf.cell(widths[i], 8, header, 1, 0, 'C', True)
        self.pdf.ln()
        
        # Table rows
        self.pdf.set_font('Arial', '', 9)
        total = 0
        
        for line in lines_data:
            motif = line.get('motif', '')[:35]  # Truncate long text
            prix = line.get('prix_unitaire', 0)
            quantite = line.get('quantite', 0)
            montant = line.get('montant_total', 0)
            total += montant
            
            self.pdf.cell(widths[0], 6, motif, 1, 0, 'L')
            self.pdf.cell(widths[1], 6, f"{prix:,.2f} DH", 1, 0, 'R')
            self.pdf.cell(widths[2], 6, f"{quantite:,.2f}", 1, 0, 'R')
            self.pdf.cell(widths[3], 6, f"{montant:,.2f} DH", 1, 0, 'R')
            self.pdf.ln()
        
        # Total row
        self.pdf.set_font('Arial', 'B', 9)
        self.pdf.set_fill_color(220, 220, 220)
        self.pdf.cell(widths[0] + widths[1] + widths[2], 8, "TOTAL", 1, 0, 'R', True)
        self.pdf.cell(widths[3], 8, f"{total:,.2f} DH", 1, 1, 'R', True)
        
        self.pdf.ln(8)
    
    def _add_invoices_summary(self, invoices_data: List[Dict]):
        """Add invoices summary section"""
        if not invoices_data:
            return
        
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 8, "Résumé des Factures", 0, 1, 'L')
        self.pdf.ln(3)
        
        # Table header
        self.pdf.set_font('Arial', 'B', 9)
        self.pdf.set_fill_color(240, 240, 240)
        
        headers = ["Date", "Fournisseur", "Montant"]
        widths = [40, 100, 35]
        
        for i, header in enumerate(headers):
            self.pdf.cell(widths[i], 8, header, 1, 0, 'C', True)
        self.pdf.ln()
        
        # Table rows
        self.pdf.set_font('Arial', '', 9)
        total_invoices = 0
        
        for invoice in invoices_data:
            date_facture = self._format_date(invoice.get('date_facture', ''))
            fournisseur = invoice.get('fournisseur', '')[:45]  # Truncate long text
            montant = invoice.get('montant_total', 0)
            total_invoices += montant
            
            self.pdf.cell(widths[0], 6, date_facture, 1, 0, 'C')
            self.pdf.cell(widths[1], 6, fournisseur, 1, 0, 'L')
            self.pdf.cell(widths[2], 6, f"{montant:,.2f} DH", 1, 0, 'R')
            self.pdf.ln()
        
        # Total row
        self.pdf.set_font('Arial', 'B', 9)
        self.pdf.set_fill_color(220, 220, 220)
        self.pdf.cell(widths[0] + widths[1], 8, f"TOTAL ({len(invoices_data)} factures)", 1, 0, 'R', True)
        self.pdf.cell(widths[2], 8, f"{total_invoices:,.2f} DH", 1, 1, 'R', True)
        
        self.pdf.ln(8)
    
    def _add_footer(self):
        """Add footer to PDF"""
        self.pdf.set_y(-20)
        self.pdf.set_font('Arial', 'I', 8)
        self.pdf.set_text_color(128, 128, 128)
        self.pdf.cell(0, 6, "Système de Gestion de Projets & Charges", 0, 1, 'C')
        self.pdf.cell(0, 6, f"Page {self.pdf.page_no()}", 0, 1, 'C')
    
    def _format_date(self, date_str: str) -> str:
        """Format date string for display"""
        if not date_str:
            return "N/A"
        
        try:
            # Try to parse different date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%d/%m/%Y')
                except ValueError:
                    continue
            return str(date_str)
        except:
            return str(date_str)


def generate_invoice_pdf(invoice_data: Dict, lines_data: List[Dict], 
                        project_name: str, output_path: str = None) -> str:
    """Convenience function to generate invoice PDF"""
    generator = ProjectPDFGenerator()
    return generator.generate_invoice_pdf(invoice_data, lines_data, project_name, output_path)


def generate_project_report_pdf(project_data: Dict, invoices_data: List[Dict], 
                              output_path: str = None) -> str:
    """Convenience function to generate project report PDF"""
    generator = ProjectPDFGenerator()
    return generator.generate_project_report_pdf(project_data, invoices_data, output_path)