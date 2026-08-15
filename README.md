# Enterprise IAM Lab: Workforce Directory & Identity Governance

## 🚀 Project Overview
This project simulates a production-grade corporate Identity Provider (IdP) architecture. It establishes strict access boundaries and automates user lifecycle onboarding matching enterprise regulatory frameworks.

## 🛠️ Tech Stack & Infrastructure
- **Identity Provider (IdP):** Keycloak 24.0 (Red Hat Open Source Engine)
- **Deployment Structure:** Containerized via Docker inside a Cloud Linux Instance
- **Networking Posture:** Configured with an edge-reverse proxy abstraction (`KC_PROXY=edge`)

## 🛡️ Implemented Identity Policies
1. **Password Governance (NIST SP 800-63B Aligned):** 
   - Mandatory minimum length of 14 characters.
   - Enforced alphanumeric/special character entropy criteria.
   - Restricted identity leakage vectors (blocked matching username strings).
2. **Brute-Force Velocity Controls:**
   - Account lockdown triggered instantly on the 5th sequential authentication failure.
   - 15-minute operational cooldown threshold.
3. **Access Control Model:**
   - Deployed **Role-Based Access Control (RBAC)** defining clear business scopes (`HR-Manager`, `IT-Admin`).
4. **Step-Up Authentication Framework:**
   - Enforced conditional user workflows using **Multi-Factor Authentication (MFA / TOTP)**