import sqlite3
import time
from ldap3 import Server, Connection, ALL

# --- CONFIGURATION SETTINGS ---
LDAP_SERVER = 'ldap://openldap:389'
LDAP_USER = 'cn=admin,dc=company.com'
LDAP_PASSWORD = 'admin_ldap_pass'

def init_hr_database():
    """Simulates the company's HR Employee database (Source of Truth)"""
    conn = sqlite3.connect('hr_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            department TEXT,
            status TEXT DEFAULT 'ACTIVE'
        )
    ''')
    
    # Seed new hires if database is completely empty
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone() == 0:
        cursor.execute("INSERT INTO employees (first_name, last_name, department, status) VALUES ('Alex', 'Admin', 'IT', 'ACTIVE')")
        cursor.execute("INSERT INTO employees (first_name, last_name, department, status) VALUES ('John', 'Doe', 'HR', 'ACTIVE')")
        conn.commit()
    conn.close()

def process_hr_pipeline():
    """Scans HR DB and pushes adjustments directly into OpenLDAP"""
    print("[IGA PIPELINE] Scanning HR Database for changes...", flush=True)
    
    conn = sqlite3.connect('hr_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name, department, status FROM employees")
    employees = cursor.fetchall()
    
    # Establish connection to the directory container
    server = Server(LDAP_SERVER, get_info=ALL)
    with Connection(server, LDAP_USER, LDAP_PASSWORD, auto_bind=True) as ldap_conn:
        
        for emp in employees:
            first, last, dept, status = emp
            username = f"{first.lower()}.{last.lower()}"
            user_dn = f"cn={username},ou=users,dc=company.com"
            email = f"{username}@company.com"
            
            if status == 'ACTIVE':
                # --- AUTOMATED JOINER PROCESS ---
                ldap_conn.search(user_dn, '(objectClass=*)')
                if not ldap_conn.entries:
                    print(f"[JOINER] Provisioning account for {username}...", flush=True)
                    # Create the LDAP account entry structure
                    ldap_conn.add(user_dn, attributes={
                        'objectClass': ['inetOrgPerson', 'organizationalPerson', 'person'],
                        'sn': last,
                        'givenName': first,
                        'cn': username,
                        'mail': email,
                        'userPassword': 'InitialSecurePassword2026!'
                    })
            
            elif status == 'TERMINATED':
                # --- AUTOMATED LEAVER PROCESS ---
                print(f"[LEAVER] Revoking access for account: {username}...", flush=True)
                ldap_conn.delete(user_dn)
                
    conn.close()

if __name__ == '__main__':
    init_hr_database()
    while True:
        try:
            process_hr_pipeline()
        except Exception as e:
            print(f"[ERROR] Pipeline encountered an issue: {e}", flush=True)
        time.sleep(30) # Check for HR changes every 30 seconds
