import sqlite3
from sqlite3 import Error


def create_connection(db_file="gestion_projets.db"):
    """Create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite version: {sqlite3.sqlite_version}")
        return conn
    except Error as e:
        print(f"Connection error: {e}")
        return None


def create_tables(conn):
    """Create all database tables if they don't exist"""
    if conn is None:
        print("No database connection")
        return
    try:
        cursor = conn.cursor()

        # Projet table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Projet (
                id_projet INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_projet TEXT NOT NULL,
                date_estimation TEXT,
                date_lancement TEXT,
                budget_max REAL NOT NULL,
                montant_investi REAL DEFAULT 0
            )
        ''')

        # FactureCharge table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS FactureCharge (
                id_facture_charge INTEGER PRIMARY KEY AUTOINCREMENT,
                id_projet INTEGER NOT NULL,
                date_facture TEXT NOT NULL,
                fournisseur TEXT NOT NULL,
                montant_total REAL NOT NULL,
                FOREIGN KEY (id_projet) REFERENCES Projet (id_projet)
            )
        ''')

        # LigneCharge table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS LigneCharge (
                id_ligne INTEGER PRIMARY KEY AUTOINCREMENT,
                id_facture_charge INTEGER NOT NULL,
                motif TEXT NOT NULL,
                prix_unitaire REAL NOT NULL,
                quantite REAL NOT NULL,
                montant_total REAL NOT NULL,
                FOREIGN KEY (id_facture_charge) REFERENCES FactureCharge (id_facture_charge)
            )
        ''')

        # Utilisateur table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Utilisateur (
                id_user INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('Directeur', 'Employe'))
            )
        ''')

        conn.commit()
        print("All tables created or already exist")
    except Error as e:
        print(f"Table creation error: {e}")


# CRUD for Projet
def create_projet(conn, projet):
    """Create a new project with (nom_projet, date_estimation, date_lancement, budget_max, montant_investi)"""
    if conn is None:
        print("No database connection")
        return None
    if len(projet) != 5:
        print("Invalid projet data: must provide 5 elements")
        return None
    sql = ''' INSERT INTO Projet(nom_projet, date_estimation, date_lancement, budget_max, montant_investi)
              VALUES(?,?,?,?,?) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, projet)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(f"Error creating project: {e}")
        return None


def read_projets(conn):
    """Read all projects"""
    if conn is None:
        print("No database connection")
        return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Projet")
        return cur.fetchall()
    except Error as e:
        print(f"Error reading projects: {e}")
        return []


def update_projet(conn, projet):
    """Update a project with (nom_projet, date_estimation, date_lancement, budget_max, montant_investi, id_projet)"""
    if conn is None:
        print("No database connection")
        return False
    if len(projet) != 6:
        print("Invalid projet data: must provide 6 elements including id_projet")
        return False
    sql = ''' UPDATE Projet
              SET nom_projet = ?,
                  date_estimation = ?,
                  date_lancement = ?,
                  budget_max = ?,
                  montant_investi = ?
              WHERE id_projet = ? '''
    try:
        cur = conn.cursor()
        cur.execute(sql, projet)
        conn.commit()
        return cur.rowcount > 0
    except Error as e:
        print(f"Error updating project: {e}")
        return False


def delete_projet(conn, id_projet):
    """Delete a project by id"""
    if conn is None:
        print("No database connection")
        return False
    sql = 'DELETE FROM Projet WHERE id_projet=?'
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_projet,))
        conn.commit()
        return cur.rowcount > 0
    except Error as e:
        print(f"Error deleting project: {e}")
        return False


# CRUD for FactureCharge
def create_facture_charge(conn, facture):
    """Create a new facture charge with (id_projet, date_facture, fournisseur, montant_total)"""
    if conn is None:
        print("No database connection")
        return None
    if len(facture) != 4:
        print("Invalid facture data: must provide 4 elements")
        return None
    sql = ''' INSERT INTO FactureCharge(id_projet, date_facture, fournisseur, montant_total)
              VALUES(?,?,?,?) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, facture)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(f"Error creating facture charge: {e}")
        return None


# CRUD for Utilisateur
def add_user(username, password, role):
    """Add a new user to the database"""
    conn = create_connection()
    if conn is None:
        print("No database connection")
        return None
    
    sql = ''' INSERT INTO Utilisateur(username, password, role)
              VALUES(?,?,?) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (username, password, role))
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(f"Error creating user: {e}")
        return None
    finally:
        conn.close()


def get_user_by_username(username):
    """Get user by username"""
    conn = create_connection()
    if conn is None:
        return None
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Utilisateur WHERE username = ?", (username,))
        return cur.fetchone()
    except Error as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        conn.close()


def get_all_users():
    """Get all users"""
    conn = create_connection()
    if conn is None:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Utilisateur")
        return cur.fetchall()
    except Error as e:
        print(f"Error getting users: {e}")
        return []
    finally:
        conn.close()


def update_user_role(conn, user_id, new_role):
    """Update user role"""
    if conn is None:
        return False
    
    sql = ''' UPDATE Utilisateur SET role = ? WHERE id_user = ? '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (new_role, user_id))
        conn.commit()
        return cur.rowcount > 0
    except Error as e:
        print(f"Error updating user role: {e}")
        return False


# CRUD for LigneCharge
def create_ligne_charge(conn, ligne):
    """Create a new ligne charge with (id_facture_charge, motif, prix_unitaire, quantite, montant_total)"""
    if conn is None:
        print("No database connection")
        return None
    if len(ligne) != 5:
        print("Invalid ligne data: must provide 5 elements")
        return None
    
    sql = ''' INSERT INTO LigneCharge(id_facture_charge, motif, prix_unitaire, quantite, montant_total)
              VALUES(?,?,?,?,?) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, ligne)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(f"Error creating ligne charge: {e}")
        return None


def read_lignes_charge_by_facture(conn, id_facture_charge):
    """Read all ligne charges for a specific facture"""
    if conn is None:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM LigneCharge WHERE id_facture_charge = ?", (id_facture_charge,))
        return cur.fetchall()
    except Error as e:
        print(f"Error reading ligne charges: {e}")
        return []


def read_factures_by_projet(conn, id_projet):
    """Read all factures for a specific project"""
    if conn is None:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM FactureCharge WHERE id_projet = ?", (id_projet,))
        return cur.fetchall()
    except Error as e:
        print(f"Error reading factures: {e}")
        return []


# Function to update montant_investi in Projet
def update_montant_investi(conn, id_projet):
    """Update montant_investi in Projet based on sum of FactureCharge montant_total"""
    if conn is None:
        print("No database connection")
        return False
    try:
        cur = conn.cursor()
        cur.execute('''
            UPDATE Projet
            SET montant_investi = (
                SELECT COALESCE(SUM(montant_total), 0) FROM FactureCharge WHERE id_projet = ?
            )
            WHERE id_projet = ?
        ''', (id_projet, id_projet))
        conn.commit()
        return cur.rowcount > 0
    except Error as e:
        print(f"Error updating montant_investi: {e}")
        return False


if __name__ == "__main__":
    conn = create_connection()
    if conn:
        create_tables(conn)
        # Test with sample data
        new_projet = ("Pont Rabat", "2025-09-01", "2025-09-15", 10000000.0, 0.0)
        project_id = create_projet(conn, new_projet)
        if project_id:
            print(f"Created project with ID: {project_id}")
            # Test facture charge
            new_facture = (project_id, "2025-09-02", "Fournisseur A", 50000.0)
            facture_id = create_facture_charge(conn, new_facture)
            if facture_id:
                print(f"Created facture charge with ID: {facture_id}")
                # Update montant_investi
                if update_montant_investi(conn, project_id):
                    print(f"Updated montant_investi for project ID {project_id}")
                    # Read and print projects to verify
                    projets = read_projets(conn)
                    print("Projects:", projets)
        conn.close()
