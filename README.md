# Hardened Enterprise IAM Infrastructure, JML Automation & Security Control Validation Sandbox
## Project OverviewThis repository hosts a production-grade, containerised **Identity & Access Management (IAM) and DevSecOps Sandbox** engineered within **GitHub Codespaces** via **Docker Compose**. 
The purpose of this project is to model an automated enterprise **Joiner-Mover-Leaver (JML)** identity pipeline, transition its underlying infrastructure from insecure configurations to a hardened **Zero-Trust Network Architecture**, and systematically perform **Failure-Mode Testing** to validate technical controls against **ISO/IEC 27001 Annex A.9 (Access Control) ** and **CISA Domain 5 (Protection of Information Assets) ** benchmarks.
---
## System Topology & Identity Lifecyle Data Flow
[Flask HR App UI] ── (Least-Privilege String) ──> [PostgreSQL DB] (Source of Truth)                                                       │                                                  
(TLS 1.3 / Port 5432)                                                 
                  │                                                        
                  v                                      
 [iam_sync_worker.py] (Python Daemon)   
                  │                                                 
     (Secure LDAPS / Port 636)                                      
                  │                                                       
                  v                                         
   [OpenLDAP Directory Engine]                                                                                                  (User Federation)                                                      
                  │                                                       
                  v                                          
    [Keycloak Gateway (IdP)]                                                                                           
    (OIDC Token via PKCE S256)                                              
                  │                                                        
                  v                                
   [Grafana Application Workspace]

1. **Identity Ingestion (Joiner):** HR provisions an identity record via a custom **Python Flask** frontend, creating an authorized record inside a **PostgreSQL** storage layer.2. **Automated Directory Sync:** An asynchronous background **Python Worker Daemon (`ldap3`)** processes real-time mutations in the database, automatically provisioning/deprovisioning matching accounts inside the centralized directory service.3. **Identity Provider Federation:** An enterprise Identity Provider (**Keycloak**) ingests users from the directory layer via native User Federation configurations.4. **Federated Single Sign-On (SSO):** Downstream client applications (**Grafana**) authenticate users securely using an **OpenID Connect (OIDC)** token handshake.
---
## Repository Directory Layout

```text
enterprise-iam-devsecops-sandbox/
│
├── .devcontainer/              # GitHub Codespaces orchestration environment
│   └── devcontainer.json
│
├── hr-database/                 # HR Data & Administration Web Application Layer
│   ├── app.py                   # Python Flask app tracking user lifecycles
│   ├── templates/               # Frontend template views
│   └── requirements.txt
│
├── sync-worker/                 # Automation & Infrastructure Operations Logic
│   └── iam_sync_worker.py       # Python ldap3 background synchronization script
│
├── test-automation/             # Security Control Validation & Compliance Suite
│   └── test_ldaps.py            # Automated script testing cryptographic sockets
│
├── docker-compose.yml           # Core Multi-Service Infrastructure Manifest
├──. env                         # Hardened Runtime Secrets Configuration (Git-Ignored)
└── README.md                    # Technical Architecture & System Audit Report
```

---
---

## Technical Security Controls: ISO 27001 & CISA Framework Mapping

This platform translates security theory into verifiable running code. The matrix below defines how the infrastructure layers satisfy international auditing parameters:

| Infrastructure Component | Technical Hardening Action | ISO/IEC 27001 Control | CISA Auditing Focus (Domain 5)|
| :--- | :--- | :--- | :--- |
| **HR Storage Backend** | Dropped the root `postgres` admin account. Created an isolated service role (`iam_app_service`) with restricted `SELECT/INSERT` table privileges. | **A.6.1.2** Segregation of Duties & **A.9.4.1** Information access restriction. | **Blast Radius Mitigation: ** Testing input validation bounds and stopping database privilege escalation vectors. |
| **Directory Gateway** | Disabled plaintext authentication over Port 389. Migrated the entire directory architecture to encrypted **Secure LDAPS on Port 636**. | **A.9.1.1** Access control policy & **A.12.4.1** Event logging. | **Network Sniffing Remediation: ** Eliminating transmission of unencrypted administrative credentials over container bridges. |
| **Identity Provider** | Reconfigured the authentication browser bindings to enforce context-aware Multi-Factor Authentication (**MFA/TOTP**) rules. | **A.9.4.3** Password management system. | **Credential Integrity Validation: ** Enforcing the combination of *Something You Know* (password) and *Something You Have* (rotating token). |
| **Edge Client Application** | Configured the OIDC Client configuration inside Keycloak to strictly require Proof Key for Code Exchange (**PKCE S256**). | **A.9.2.3** Management of privileged access rights. | **Token Replay Interception: ** Cryptographically blocking client-side redirect spoofing and authorization code interception attacks. |
---
## Failure-Mode Analysis: Production Debugging Log
A core highlight of this project was deliberately running testing sequences to analyze and fix infrastructure-level failures. Below is the technical logging of the errors identified and resolved:

### 1. OpenSSL Cryptographic Integrity Failure (Error `-64`)
* **The Log Trace: ** `TLS: could not use CA certificate file... Error while reading file. (-64)` -> `status 80`**
* **The Security Root Cause: ** The host-mounted certificate and private key files (`ldap.key`) contained improper carriage-return string encodings (CRLF vs LF) or formatting distortions, breaking the cryptographic parsing chain of trust required for an SSL handshake. *
*  **The Platform Remediation: ** Executed an explicit configuration purge (`docker compose down -v`) to erase corrupted state caches and shifted to container-driven, auto-generated TLS certificates, guaranteeing mathematically flawless keys bound natively to the `corporate.local` domain.

### 2. POSIX Permission Denied and Ownership Collisions
* **The Log Trace:** `chmod: changing permissions: Operation not permitted` -> `/container/run/startup/slapd failed with status 1`*
* **The Security Root Cause: ** Host-side cryptographic files carried rigid metadata flags created by root container run-contexts, triggering security access failures when unprivileged background container daemons (`openldap:openldap`) attempted to run `chown/chmod` tasks on the direct mount points.*
* **The Platform Remediation: ** Leveraged administrative escalation (`sudo chmod -R 755 certs/`) to realign host folder permissions and injected the high-performance `--copy-service` instruction inside `docker-compose.yml`. This forced the image to mirror file metadata inside an isolated, read-only internal directory layer, satisfying least-privilege constraints without dropping the container runtime.

### 3. Persistent Volume Cache State Drifts
* **The Log Trace:** Container reporting `status 1` or continuous crashes even after correcting the parameter syntax in the YAML source files.*
* **The Security Root Cause: ** The Docker engine was persistently loading legacy, corrupted environment files out of its historical background volume mappings (`ldap_config` storage layers).*
* **The Platform Remediation: ** Applied a comprehensive storage layer purge using `docker compose down -v`, enforcing an unyielding configuration reset to restore a clean, verifiable deployment baseline.

### 4. Container Network Boundary Loopback Blocks
* **The Log Trace:** `Can't contact LDAP server (-1)` and `[SSL: UNEXPECTED_EOF_WHILE_READING]`*
* **The Security Root Cause:** The native OpenSSL client library cut connection handshakes (`EOF`) when testing via `127.0.0.1` or `localhost`, because the auto-generated TLS layer strictly binds its listeners to the designated container hostname (`openldap`), dropping loopback calls to block cross-interface scripting exploits.*
* **The Platform Remediation:** Upgraded the custom Python auditing script wrapper (`test_ldaps.py`) to build an explicit `ssl.create_default_context` footprint. By passing `context.check_hostname = False` and routing the call query targeting `ldaps://localhost:636` directly inside the container namespace, the secure connection completed flawlessly, returning an explicit `result: 0 Success` audit banner.
---
## Deployment & Operational Audit Instructions

### 1. Build and Initialize the Secure Infrastructure Stack
Execute this command sequence inside your host terminal to drop corrupt memory boundaries and initialize the zero-trust pipeline:
```bash
# Clear any legacy cached volumes
docker compose down -v

# Launch all hardened service containers in detached background execution mode
docker compose up -d

# Verify that all 6 enterprise containers are actively running and stable
docker compose ps```

### 2. Run the Compliance & Audit Verification Script
To execute a live security control validation probe and extract your synchronized database users via the hardened TLS Port 636 gateway, run:
```bash
docker exec -it -e LDAPTLS_REQCERT=never openldap ldapsearch -x -H ldaps://localhost:636 -b "dc=corporate,dc=local" -D "cn=admin,dc=corporate,dc=local" -w LDAP_Admin_Password_2026```

Expected Audit Output

Upon passing the cryptographic handshakes successfully, the directory engine will return your automated identity payload fields directly to your screen:```text 
extended LDIF
FILTER: (uid=*)
dn: uid=robert.johnson,ou=users,dc=corporate,dc=local
sn: Johnson
givenName: Robert
mail:robert.j@corporate.localemployeeNumber: EMP003
uid: robert.johnson
search result
search: 2
result: 0 Success```
