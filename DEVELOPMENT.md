# Development Guide

## 🚀 Quick Start

### First Time Setup
1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   ```bash
   python setup.py
   ```

3. **Run Application**
   ```bash
   python main.py
   ```
   Or use the provided scripts:
   - Windows: `run_app.bat`
   - PowerShell: `run_app.ps1`

## 📁 Project Structure

### Core Application (`app/`)
- `auth.py` - User authentication and password hashing
- `db.py` - Database operations and connections
- `models.py` - Business logic and data models
- `utils.py` - Utility functions and helpers
- `pdf_generator.py` - PDF report generation using ReportLab

### GUI Components (`app/gui/`)
- `login.py` - Login interface (SignInDialog)
- `main_window.py` - Main application window
- `project_form.py` - Project creation/editing forms
- `project_details.py` - Project detail views
- `invoice_form.py` - Invoice management interface

### Assets
- `Images/` - Logo and image assets
- `gestion_projets.db` - SQLite database file

## 🔧 Development Guidelines

### Code Organization
- Follow Python PEP 8 style guidelines
- Use type hints where applicable
- Keep GUI logic separate from business logic
- Document complex functions with docstrings

### Database Schema
The application uses SQLite with the following tables:
- `Utilisateur` - User accounts and roles
- `Projet` - Project information
- `FactureCharge` - Invoice/charge records
- `LigneCharge` - Individual charge line items

### User Roles
- **Directeur** - Full access (create, read, update, delete)
- **Employe** - Read-only access

### Default Users
- `directeur/directeur123` (Director role)
- `employe/employe123` (Employee role)
- `admin/admin123` (Director role)

## 🛠️ Maintenance

### Adding New Features
1. Create feature branch
2. Implement in appropriate module
3. Update GUI if needed
4. Test thoroughly
5. Update documentation

### Database Changes
1. Modify `db.py` schema
2. Create migration script if needed
3. Update `setup.py` if required
4. Test with fresh database

### Clean Development Environment
- Use `.gitignore` to prevent clutter
- Run `python setup.py` for fresh start
- Remove `__pycache__/` directories regularly
- Keep test files in separate branch

## 📦 Distribution

### Creating Release
1. Ensure all functionality works
2. Clean project structure
3. Update version in `main.py`
4. Create distribution package
5. Include setup instructions

### File Exclusions (for distribution)
- `__pycache__/` directories
- `.git/` directory
- `.idea/`, `.vscode/` IDE configs
- `test_*.py` test files
- Generated PDF files
- Log files
