import os
import time
import psycopg2
import ssl
from ldap3 import Server, Connection, ALL, Tls

# Extract operational configs from environment variables
DB_HOST = os.getenv('DB_HOST', 'hr-db')
DB_NAME = os.getenv('DB_NAME', 'hr_database')
DB_USER = os.getenv('DB_USER', 'hr_admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'HR_Secure_Password_2026')

LDAP_SERVER = os.getenv('LDAP_SERVER', 'openldap')
LDAP_BIND_DN = os.getenv('LDAP_BIND_DN', 'cn=admin,dc=corporate,dc=local')
LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PASSWORD', 'LDAP_Admin_Password_2026')

def sync_to_ldap():
    try:
        # Realtime scan heartbeat indicator
        print("[SYNC] Scanning HR database for updates...", flush=True)

        # Establish connections to PostgreSQL and OpenLDAP
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()
        tls = Tls(ca_certs_file='./ca.crt', validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1_2)
        server = Server(LDAP_SERVER, port=636, get_info=ALL, use_ssl=True, tls=tls)
        conn_ldap = Connection(server, user=LDAP_BIND_DN, password=LDAP_BIND_PASSWORD, auto_bind=True)

        # 1. Fetch employee data from Postgres matching your explicit schema columns
        cursor.execute("SELECT emp_id, first_name, last_name, email, status FROM employees;")
        for user in cursor.fetchall():
            emp_id, f_name, l_name, email, status = user
            username = f"{f_name.lower()}.{l_name.lower()}"
            dn = f"uid={username},ou=users,dc=corporate,dc=local"

            # 2. Lifecycle Handling: Provision Active Accounts
            if status == 'ACTIVE':
                attrs = {
                    'objectClass': ['inetOrgPerson', 'top'],
                    'cn': f"{f_name} {l_name}",
                    'sn': l_name,
                    'givenName': f_name,
                    'mail': email,
                    'employeeNumber': str(emp_id)
                }
                
                try:
                    # Attempt provisioning
                    if conn_ldap.add(dn, attributes=attrs):
                        print(f"[JOINER] Successfully provisioned: {username}", flush=True)
                    else:
                        # Output the explicit directory description if it skips
                        desc = conn_ldap.result.get('description', 'Unknown reason')
                        print(f"[SYNC INFO] Skip or rejection for {username}. Result: {desc}", flush=True)
                except Exception as ldap_err:
                    print(f"[SYNC ERROR] Failed adding {username}: {ldap_err}", flush=True)

            # 3. Lifecycle Handling: Deprovision Terminated Accounts
            elif status in ['TERMINATED', 'INACTIVE']:
                try:
                    if conn_ldap.delete(dn):
                        print(f"[LEAVER] Successfully offboarded: {username}", flush=True)
                except Exception as ldap_del_err:
                    print(f"[SYNC ERROR] Failed offboarding {username}: {ldap_del_err}", flush=True)

        # Graceful cleanup at loop end outside user logic
        cursor.close()
        conn.close()
        conn_ldap.unbind()
    except Exception as e:
        print(f"Pipeline Running... (Internal Sync Status: {e})", flush=True)

if __name__ == "__main__":
    print("Waiting 10 seconds for core directory initialization...", flush=True)
    time.sleep(10)
    
    # Initialization Check: Auto-create missing Organizational Units safely
    print("[INIT] Verifying corporate layout tree OUs...", flush=True)
    try:
        server = Server(LDAP_SERVER, get_info=ALL)
        conn_init = Connection(server, user=LDAP_BIND_DN, password=LDAP_BIND_PASSWORD, auto_bind=True)
        for ou in ['users', 'groups']:
            conn_init.search(search_base='dc=corporate,dc=local', search_filter=f"(ou={ou})")
            if not conn_init.entries:
                if conn_init.add(f"ou={ou},dc=corporate,dc=local", attributes={'objectClass': ['organizationalUnit'], 'ou': ou}):
                    print(f"[INIT] Created missing organizational unit: ou={ou}", flush=True)
        conn_init.unbind()
    except Exception as e:
        print(f"[INIT INFO] Corporate layout check complete. Status: {e}", flush=True)

    print("Automated IAM Sync Engine Active.", flush=True)
    while True:
        sync_to_ldap()
        time.sleep(5)

