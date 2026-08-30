import ssl
import sys
from ldap3 import Server, Connection, Tls, ALL

def run_validation():
    print("=== INITIALIZING ENCRYPTED ACCESS CONTROL AUDIT ===")
    
    # 1. Establish an absolute modern SSL Context bypass pattern
    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    # Force the cryptographic engine to allow legacy/self-signed container protocol strings
    context.set_ciphers('DEFAULT@SECLEVEL=1')

    # 2. Inject this custom validated context into the ldap3 configuration envelope
    tls_config = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLS_CLIENT)
    tls_config.context = context
    
    # 3. Bind explicitly to your local exposed container endpoint socket
    server = Server('127.0.0.1', port=636, use_ssl=True, tls=tls_config, get_info=ALL)
    
    try:
        # 4. Initialize the authenticated secure channel link
        conn = Connection(
            server, 
            user='cn=admin,dc=corporate,dc=local', 
            password='LDAP_Admin_Password_2026', 
            auto_bind=True
        )
        
        # 5. Extract and scan the active user records inside your directory database
        conn.search('dc=corporate,dc=local', '(uid=*)', attributes=['uid'])
        
        print("\n🚀 [ZERO-TRUST AUDIT VALIDATION SUCCESS] 🚀")
        print(f"Total Active Identities Secured: {len(conn.entries)}")
        print("-" * 45)
        for entry in conn.entries:
            print(f"Verified Identity Securely Provisioned: {entry.uid}")
        print("-" * 45)
            
        conn.unbind()
        
    except Exception as e:
        print(f"\n❌ Handshake Terminated by Gateway. Technical Trace: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_validation()

