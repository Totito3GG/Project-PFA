# Système de Gestion de Projets & Charges

## Description
Application complète de gestion de projets et de suivi des charges pour entreprises de BTP, construction, etc. Permet le suivi budgétaire, la gestion des factures, la génération de rapports PDF, et le contrôle d'accès par rôle (Directeur/Employe).

## Fonctionnalités
- ✅ **Gestion des Projets** : CRUD complet avec suivi budgétaire
- ✅ **Gestion des Factures** : Création et suivi des charges par projet
- ✅ **Authentification** : Système de login avec rôles (Directeur/Employe)
- ✅ **Interface Moderne** : Interface PyQt5 avec design professionnel
- ✅ **Rapports PDF** : Génération automatique de rapports et factures
- ✅ **Base de Données** : SQLite avec relations complètes
- ✅ **Calculs Automatiques** : Suivi du budget restant et pourcentages

## Technologies
- **Python 3.7+** (Compatible avec Python 3.13.7)
- **SQLite** : Base de données locale
- **PyQt5** : Interface graphique moderne
- **fpdf2** : Génération de rapports PDF

## Installation et Lancement

### 1. Prérequis
- Python 3.7 ou supérieur (recommandé: Python 3.13.7)
- pip (gestionnaire de paquets Python)

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 3. Initialisation de la base de données
```bash
python setup.py
```
Ce script va :
- Créer la base de données SQLite
- Créer les tables nécessaires
- Ajouter des utilisateurs par défaut

### 4. Lancement de l'application
```bash
python main.py
```

## Utilisateurs par défaut
- **Directeur** : `directeur` / `directeur123`
- **Employe** : `employe` / `employe123`
- **Admin** : `admin` / `admin123`

## Structure du Projet
```
├── app/
│   ├── auth.py              # Authentification et sécurité
│   ├── db.py                # Gestion de la base de données
│   ├── models.py            # Modèles métier
│   ├── utils.py             # Fonctions utilitaires
│   ├── pdf_generator.py     # Génération de PDF
│   └── gui/
│       ├── login.py         # Interface de connexion
│       ├── main_window.py   # Fenêtre principale
│       ├── project_form.py  # Formulaire de projet
│       ├── project_details.py # Détails de projet
│       └── invoice_form.py  # Formulaire de facture
├── Images/                  # Images et logos
├── main.py                  # Point d'entrée de l'application
├── setup.py                 # Script d'initialisation
├── requirements.txt         # Dépendances Python
├── run_app.bat             # Script de lancement Windows
├── run_app.ps1             # Script PowerShell
└── README.md               # Ce fichier
```

## Utilisation

### Pour les Directeurs
- **Gestion complète** : Créer, modifier, supprimer projets et factures
- **Rapports** : Générer des rapports PDF détaillés
- **Suivi budgétaire** : Visualiser l'état des budgets en temps réel

### Pour les Employes
- **Consultation** : Voir tous les projets et factures
- **Rapports** : Générer des rapports de consultation
- **Lecture seule** : Accès en consultation uniquement

## Exemple d'utilisation
1. **Connexion** : Utilisez les identifiants par défaut
2. **Créer un projet** : Cliquez sur "Nouveau Projet" dans l'onglet Projets
3. **Ajouter une facture** : Cliquez sur "Nouvelle Facture" dans l'onglet Factures
4. **Générer un rapport** : Sélectionnez un projet et cliquez sur "Exporter Rapport"

## Base de Données
L'application utilise SQLite avec 4 tables principales :
- **Projet** : Informations des projets
- **FactureCharge** : Factures liées aux projets
- **LigneCharge** : Détail des lignes de facturation
- **Utilisateur** : Gestion des utilisateurs et rôles

## Support
Pour toute question ou problème, consultez le code source ou créez une issue sur le repository du projet.
