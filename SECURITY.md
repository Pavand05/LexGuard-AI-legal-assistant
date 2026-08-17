# LexGuard-MA: Security & Data Privacy Policy

## 1. Compliance with Digital Personal Data Protection Act (DPDP Act 2023)
- **Data Minimization**: LexGuard-MA extracts only clauses and metadata necessary for legal analysis.
- **Privacy Mode Redaction**: In Privacy Mode, personal identifiers including Indian Aadhaar numbers, PAN cards, bank account numbers, phone numbers, and emails are masked in memory prior to downstream summarization.
- **Zero Third-Party Training Leakage**: Document data processed through local deterministic pipelines and API endpoints is never used to train generalized models.

## 2. IT Act 2000 & Reasonable Security Practices (Section 43A)
- **Authentication & RBAC**: JWT token protection with strict role-based access control (`client`, `lawyer`, `admin`).
- **Encrypted Communication**: HTTPS/TLS end-to-end transport and bcrypt password hashing (12 rounds).
- **SQL Injection & XSS Prevention**: Parameterized ORM queries via SQLAlchemy and React JSX auto-escaping for HTML templates.
