"""
Run this script once to seed sample documents into the RAG index.
Usage:  python seed_data.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from rag_engine import RAGEngine

DOCS = [
    # ── Employee-accessible ───────────────────────────────────────────────
    {
        "role": "employee",
        "filename": "employee_handbook.txt",
        "text": """
Employee Handbook - General Policies

Welcome to the company! This handbook outlines the key policies and guidelines
for all employees.

Working Hours:
Our standard working hours are 9:00 AM to 6:00 PM, Monday through Friday.
Flexible arrangements may be available with manager approval.
Employees are entitled to a 1-hour lunch break.

Leave Policy:
Annual Leave: 20 days per year for employees with less than 5 years of service.
              25 days per year for employees with 5+ years of service.
Sick Leave: 10 days per year with medical certificate for absences over 3 consecutive days.
Maternity/Paternity Leave: As per local government regulations.

Code of Conduct:
All employees are expected to maintain professional conduct at all times.
Harassment, discrimination, or bullying will not be tolerated and may result in termination.
Confidential company information must not be shared outside the organisation.

Remote Work Policy:
Employees may work remotely up to 2 days per week with manager approval.
Remote workers must maintain core hours of 10 AM - 4 PM for team collaboration.
Company equipment must be used securely with VPN enabled when working remotely.

Performance Reviews:
Performance reviews are conducted bi-annually in June and December.
Employees should prepare a self-assessment report before each review.

IT and Data Policy:
Company laptops and devices must not be used for personal activities.
All data must be stored on approved company systems.
Report any security incidents immediately to the IT helpdesk.
""",
    },
    {
        "role": "employee",
        "filename": "work_policies.txt",
        "text": """
Company Work Policies 2024

Attendance Policy:
Employees must inform their manager at least 30 minutes before the start of their shift if they are unable to attend.
Three or more unexplained absences in a month may result in a formal warning.

Communication Policy:
Official communication should be via company email or the approved messaging platform.
Personal social media must not be used to discuss company matters.
All external communications on behalf of the company must be approved by management.

Expense Policy:
Work-related expenses must be submitted within 30 days of being incurred.
Expenses over $500 require pre-approval from department head.
Receipts are mandatory for all claims.

Health and Safety:
Employees must follow all health and safety guidelines posted in the workplace.
Report all accidents or near-misses to HR within 24 hours.
First-aid kits are located at each floor reception.

Training and Development:
The company offers annual training budget of $1,000 per employee.
Employees should discuss training needs during performance reviews.
Mandatory compliance training must be completed by the end of Q1 each year.

Social Events:
The company organises quarterly team events.
Participation is encouraged but optional.
All events are conducted in a respectful and inclusive manner.
""",
    },
    # ── HR-accessible ─────────────────────────────────────────────────────
    {
        "role": "hr",
        "filename": "salary_information.txt",
        "text": """
Salary and Compensation Structure (CONFIDENTIAL - HR Only)

Salary Bands 2024:

Junior Engineer (L1):          $55,000 - $70,000 per annum
Mid-level Engineer (L2):       $70,000 - $90,000 per annum
Senior Engineer (L3):          $90,000 - $115,000 per annum
Lead Engineer (L4):            $115,000 - $140,000 per annum
Principal Engineer (L5):       $140,000 - $175,000 per annum

HR Roles:
HR Coordinator:                $45,000 - $60,000 per annum
HR Manager:                    $65,000 - $85,000 per annum
HR Director:                   $95,000 - $130,000 per annum

Management:
Department Head:               $120,000 - $160,000 per annum
Vice President:                $160,000 - $220,000 per annum

Bonus Structure:
Performance bonuses are paid annually in January based on year-end review scores.
Score 4-5 (Exceeds Expectations): 15-20% of base salary
Score 3 (Meets Expectations):     8-12% of base salary
Score 1-2 (Below Expectations):   0% bonus

Benefits:
Health Insurance: Company covers 80% of premium for employee and family.
Pension: Company matches up to 5% of salary contribution.
Stock Options: Available to L3 and above, vesting over 4 years.

Payroll:
Salary is paid on the last working day of each month via bank transfer.
Employees must submit timesheets by the 25th of each month.
""",
    },
    {
        "role": "hr",
        "filename": "hr_policies.txt",
        "text": """
HR Policies and Procedures (CONFIDENTIAL - HR Only)

Recruitment Policy:
All vacancies must be advertised internally for at least 5 business days before external posting.
Interview panels must include at least two interviewers.
References must be checked before formal offers are made.
Background checks are mandatory for all new hires.

Disciplinary Process:
Stage 1: Verbal Warning - documented and kept on file for 6 months.
Stage 2: Written Warning - issued for repeat offences or serious misconduct.
Stage 3: Final Written Warning - last opportunity before termination.
Stage 4: Termination - with notice period as per contract, or immediate for gross misconduct.

Grievance Procedure:
Employees should first raise concerns with their line manager.
If unresolved, escalate to HR within 10 business days.
HR will investigate and respond within 15 business days.
Appeal can be made to senior management within 5 business days of decision.

Equal Opportunities:
The company is committed to equal opportunity employment.
Discrimination based on age, gender, race, religion, disability, or sexual orientation is prohibited.
Reasonable adjustments will be made for employees with disabilities.

Confidentiality:
All HR records are strictly confidential.
Only authorised HR personnel and senior management may access personnel files.
Data retention: employment records kept for 7 years post-termination.

Employee Assistance Programme:
Free and confidential counselling service available to all employees.
Up to 6 free sessions per year.
Contact details available from HR or on the intranet.
""",
    },
    # ── Admin-accessible ──────────────────────────────────────────────────
    {
        "role": "admin",
        "filename": "security_policies.txt",
        "text": """
Infrastructure Security Policies (STRICTLY CONFIDENTIAL - Admin Only)

Server Access Credentials (DEMO - CHANGE IN PRODUCTION):
Production DB Server: prod-db-01.internal  | root | [stored in vault]
Staging Server:       stage-01.internal    | deploy | [stored in vault]
Admin Portal:         admin.internal:8443  | [SSO only]

All credentials are managed via HashiCorp Vault.
Access requests must go through the ITSM ticketing system.
MFA is mandatory for all privileged access.

Network Security:
Production network is segmented from corporate network via firewall.
All internal traffic uses mTLS with certificates rotated every 90 days.
Intrusion detection system monitors all ingress/egress traffic.
DDoS protection is enabled on all public endpoints.

Encryption Standards:
Data at rest: AES-256 encryption on all storage volumes.
Data in transit: TLS 1.3 minimum on all connections.
Database backups: encrypted and stored off-site in two geographic regions.
Encryption keys: Managed by HSM, rotated annually.

Incident Response:
P1 (Critical): Respond within 15 minutes, involve CISO.
P2 (High): Respond within 1 hour.
P3 (Medium): Respond within 4 hours.
P4 (Low): Respond within 24 hours.
All incidents must be documented in the ITSM system.

Backup Policy:
Daily incremental backups at 2 AM UTC.
Weekly full backups on Sunday at 1 AM UTC.
Backup retention: 30 days online, 1 year offline archive.
Recovery test: performed monthly, documented.

Compliance:
System is ISO 27001 certified (renewal due March 2025).
GDPR compliance audit conducted annually.
Penetration testing by external vendor twice per year.
""",
    },
    {
        "role": "admin",
        "filename": "infrastructure_docs.txt",
        "text": """
Infrastructure Architecture Documentation (ADMIN ONLY)

Production Architecture Overview:

Load Balancer:
  - AWS ALB in us-east-1 and eu-west-1
  - Health check interval: 30 seconds
  - SSL termination at load balancer
  - WAF enabled with OWASP ruleset

Application Tier:
  - 6x EC2 t3.xlarge instances (auto-scaling 4-12)
  - Docker containers orchestrated via ECS
  - Blue-green deployment strategy
  - Canary releases for major updates

Database Tier:
  - Primary: AWS RDS PostgreSQL 15 (db.r6g.xlarge)
  - Read replicas: 2x in same region, 1x cross-region
  - Automated failover with RDS Multi-AZ
  - Connection pooling via PgBouncer

Cache Layer:
  - Redis 7.x cluster (ElastiCache)
  - 3-node cluster with replication
  - Cache invalidation via event-driven pub/sub

Monitoring Stack:
  - Prometheus + Grafana for metrics
  - ELK Stack for centralised logging
  - PagerDuty for on-call alerting
  - Datadog APM for application performance

CI/CD Pipeline:
  - GitHub Actions for build and test
  - ArgoCD for GitOps deployment
  - SonarQube for code quality gates
  - Snyk for dependency vulnerability scanning

Disaster Recovery:
  - RTO: 4 hours, RPO: 1 hour
  - DR site active-passive in eu-central-1
  - Runbooks maintained in Confluence
  - DR drill conducted quarterly
""",
    },
]


def seed():
    engine = RAGEngine()
    for doc in DOCS:
        n = engine.add_document(
            text=doc["text"],
            filename=doc["filename"],
            doc_role=doc["role"],
        )
        print(f"  ✓ {doc['filename']} ({doc['role']}) → {n} chunks")
    print("\nSeeding complete! You can now start the backend.")


if __name__ == "__main__":
    seed()
