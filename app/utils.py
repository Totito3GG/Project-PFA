from datetime import datetime, date
from typing import List, Optional
import re


def format_currency(amount: float) -> str:
    """Format amount as currency with DH suffix"""
    return f"{amount:,.2f} DH"


def format_date(date_str: str) -> str:
    """Format date string for display"""
    if not date_str:
        return ""
    try:
        if isinstance(date_str, str):
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%d/%m/%Y')
                except ValueError:
                    continue
        return str(date_str)
    except:
        return str(date_str)


def parse_date(date_str: str) -> Optional[date]:
    """Parse date string to date object"""
    if not date_str:
        return None
    
    # Try different date formats
    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def validate_budget(budget_str: str) -> tuple[bool, float]:
    """Validate budget input and return (is_valid, amount)"""
    try:
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', budget_str)
        if not cleaned:
            return False, 0.0
        
        amount = float(cleaned)
        return amount >= 0, amount
    except ValueError:
        return False, 0.0


def validate_quantity(quantity_str: str) -> tuple[bool, float]:
    """Validate quantity input and return (is_valid, quantity)"""
    try:
        cleaned = re.sub(r'[^\d.]', '', quantity_str)
        if not cleaned:
            return False, 0.0
        
        quantity = float(cleaned)
        return quantity > 0, quantity
    except ValueError:
        return False, 0.0


def validate_price(price_str: str) -> tuple[bool, float]:
    """Validate price input and return (is_valid, price)"""
    try:
        cleaned = re.sub(r'[^\d.]', '', price_str)
        if not cleaned:
            return False, 0.0
        
        price = float(cleaned)
        return price >= 0, price
    except ValueError:
        return False, 0.0


def calculate_line_total(price: float, quantity: float) -> float:
    """Calculate total for a line item"""
    return price * quantity


def calculate_project_remaining_budget(budget_max: float, total_charges: float) -> float:
    """Calculate remaining budget for a project"""
    return budget_max - total_charges


def calculate_budget_percentage_used(total_charges: float, budget_max: float) -> float:
    """Calculate percentage of budget used"""
    if budget_max == 0:
        return 0.0
    return (total_charges / budget_max) * 100


def is_project_over_budget(total_charges: float, budget_max: float) -> bool:
    """Check if project is over budget"""
    return total_charges > budget_max


def get_budget_status_color(percentage_used: float) -> str:
    """Get color code based on budget usage percentage"""
    if percentage_used >= 100:
        return "#dc2626"  # Red - over budget
    elif percentage_used >= 80:
        return "#ea580c"  # Orange - warning
    elif percentage_used >= 60:
        return "#d97706"  # Amber - caution
    else:
        return "#16a34a"  # Green - good


def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username or len(username) < 3:
        return False
    # Allow alphanumeric and underscore only
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength and return (is_valid, message)"""
    if len(password) < 6:
        return False, "Le mot de passe doit contenir au moins 6 caractères"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "Le mot de passe doit contenir au moins une lettre"
    
    if not re.search(r'[0-9]', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    return True, "Mot de passe valide"


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent SQL injection"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
    sanitized = text
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()


def format_project_summary(project_data: dict) -> str:
    """Format project summary for display"""
    return f"""
Projet: {project_data.get('nom_projet', 'N/A')}
Budget prévu: {format_currency(project_data.get('budget_max', 0))}
Total dépensé: {format_currency(project_data.get('montant_investi', 0))}
Reste budget: {format_currency(project_data.get('reste_budget', 0))}
Pourcentage utilisé: {project_data.get('pourcentage_utilise', 0):.1f}%
"""


def get_current_date_str() -> str:
    """Get current date as string in YYYY-MM-DD format"""
    return datetime.now().strftime('%Y-%m-%d')


def get_current_datetime_str() -> str:
    """Get current datetime as string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length with ellipsis"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def sort_projects_by_budget(projects: List[dict], reverse: bool = False) -> List[dict]:
    """Sort projects by budget amount"""
    return sorted(projects, key=lambda x: x.get('budget_max', 0), reverse=reverse)


def sort_projects_by_usage(projects: List[dict], reverse: bool = False) -> List[dict]:
    """Sort projects by budget usage percentage"""
    return sorted(projects, key=lambda x: x.get('pourcentage_utilise', 0), reverse=reverse)