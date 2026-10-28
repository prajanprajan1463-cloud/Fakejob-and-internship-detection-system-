"""
Dataset loader and reference training samples.
NOTICE: The embedded dataset is explicitly identified as an educational synthetic
reference dataset designed for testing the training pipeline and demonstration.
For production scale, users should train on real-world benchmark datasets such as the
EMScAD (Employment Scam Aegean Dataset) or Kaggle Real / Fake Job Postings dataset.
"""

from typing import List, Dict, Tuple, Any, Optional
import pandas as pd
from pathlib import Path


SYNTHETIC_DATASET: List[Dict[str, Any]] = [
    # --- Legitimate Job Postings (Label: 0) ---
    {
        "title": "Senior Python Backend Engineer",
        "description": "We are looking for a Senior Python Backend Engineer to join our core cloud platform team. Responsibilities include designing RESTful APIs using Flask and FastAPI, optimizing PostgreSQL database queries, implementing Celery tasks, and collaborating with cross-functional product managers and front-end teams. Requirements: 4+ years of professional Python experience, strong knowledge of SQL, automated unit testing with pytest, Docker containerization, and Git. Benefits: Competitive salary, comprehensive health and dental insurance, 401(k) matching, flexible remote work policy, and 20 days paid annual leave. Equal opportunity employer.",
        "is_fraudulent": 0
    },
    {
        "title": "Junior Frontend Developer (React)",
        "description": "Acme Tech is hiring a Junior Frontend Developer. You will assist in building responsive web applications with React, TypeScript, and Tailwind CSS. You will participate in daily standups, conduct peer code reviews, and work alongside UX designers. Minimum requirements: Bachelor's degree in Computer Science, BCA, or equivalent practical experience; familiarity with JavaScript ES6+, HTML5, CSS3, and Git. The selection process consists of an initial recruiter screening call, a technical coding review, and a final team interview. We never ask candidates for fees or banking credentials.",
        "is_fraudulent": 0
    },
    {
        "title": "Human Resources Coordinator",
        "description": "Global Logistics Corp is seeking an HR Coordinator based in Chicago, IL. The coordinator handles employee onboarding, verifies I-9 documentation, coordinates corporate benefits enrollment, and organizes internal training sessions. Requirements: 2+ years HR experience, proficiency in Workday or similar HRIS, excellent written and verbal communication. This is a full-time hybrid position. Background check and standard professional references are conducted prior to final contract signing.",
        "is_fraudulent": 0
    },
    {
        "title": "Data Analyst - Business Intelligence",
        "description": "Join our analytics department to translate complex business metrics into actionable insights. Responsibilities: Building automated dashboards using PowerBI and Tableau, writing complex SQL queries against Snowflake data warehouses, and presenting quarterly KPI reports to department heads. Qualifications: Bachelor's degree in Statistics, Mathematics, Economics, or Computer Science; 2+ years experience with SQL and Python (pandas); strong presentation skills. Health insurance, wellness stipend, and parental leave included.",
        "is_fraudulent": 0
    },
    {
        "title": "Cybersecurity Operations Analyst",
        "description": "We are seeking a SOC Analyst to monitor network security alerts, investigate anomalous traffic, assist with incident response triage, and configure SIEM rules. Requirements: Familiarity with Wireshark, Splunk, TCP/IP networking, and Linux command line. CompTIA Security+ or CEH certification is preferred. The interview process includes an initial phone screen, technical assessment, and video panel interview with the security team.",
        "is_fraudulent": 0
    },
    {
        "title": "Content Marketing Specialist",
        "description": "B2B SaaS startup looking for a Content Marketing Specialist to manage our corporate blog, write technical case studies, develop email newsletters, and oversee social media channels. Must have 2+ years of content writing experience, solid understanding of SEO best practices, and familiarity with Google Analytics. Full-time position with health benefits, flexible hours, and professional development budget.",
        "is_fraudulent": 0
    },
    {
        "title": "Customer Support Representative",
        "description": "Providing tier-1 software support to enterprise customers via Zendesk ticketing and telephone. Responsibilities include diagnosing user issues, escalating software bugs to engineering, and updating knowledge base documentation. Requirements: High school diploma or associate degree, prior customer service experience, empathetic communication style. Paid 4-week training provided at our corporate office. Shift allowances and healthcare coverage included.",
        "is_fraudulent": 0
    },
    {
        "title": "DevOps / Infrastructure Engineer",
        "description": "Seeking an experienced DevOps Engineer to maintain our AWS Kubernetes clusters, manage Terraform infrastructure as code, optimize CI/CD pipelines in GitLab, and implement Prometheus monitoring. Requirements: 3+ years managing production AWS environments, experience with Docker, Bash scripting, and infrastructure automation. Competitive compensation, stock options, and comprehensive medical benefits.",
        "is_fraudulent": 0
    },

    # --- Fraudulent / Scam Job Postings (Label: 1) ---
    {
        "title": "Urgent Data Entry Operator - Earn $4500 Weekly From Home",
        "description": "URGENT HIRING! Simple online data entry and copy-paste work. Anybody can do this from home, no experience needed, housewives and students welcome! Earn $1000 to $4500 every week. Work just 1 to 2 hours per day. 100% guaranteed income with instant daily payouts. Immediate selection without any interview! To receive your employment kit and start today, candidate must pay a refundable registration and documentation fee of $150 via Western Union or Crypto. Contact our hiring manager immediately on Telegram: @quick_job_hr. Offer expires today!",
        "is_fraudulent": 1
    },
    {
        "title": "Virtual Assistant - Check Equipment Deposit Scam",
        "description": "We are hiring a Remote Personal Assistant immediately. You will be responsible for booking travel, answering emails, and purchasing office supplies. We will send you a certified company cashier's check of $4,500 to your address. You must deposit the check into your personal bank account, keep $500 as your first week salary advance, and wire the remaining $4,000 via Zelle or Bitcoin to our authorized vendor to ship your Apple MacBook and home office equipment. Hired immediately without interview.",
        "is_fraudulent": 1
    },
    {
        "title": "Telegram Customer Chat Agent - High Daily Payouts",
        "description": "Start working today! Easy work liking YouTube videos, following Instagram accounts, and rating merchant products. Earn ₹3,000 to ₹10,000 daily credited directly to your account. No resume or qualifications required. Contact HR manager immediately on WhatsApp +91-9876543210 or message directly on Telegram @TaskRewardsOfficial. Act fast, only 5 vacancies left! Immediate joining after deposit of security amount.",
        "is_fraudulent": 1
    },
    {
        "title": "Package Reshipping and Quality Inspector",
        "description": "Work from home inspect packages and ship them overseas. Receive luxury packages at your home address, inspect contents, print prepaid shipping labels, and forward packages to our overseas depot. To verify your identity and setup payroll direct deposit, you must send photos of your driver's license, social security card, and share your online banking login credentials or OTP. Start right away.",
        "is_fraudulent": 1
    },
    {
        "title": "Immediate Offer - Software Developer Intern (Training Fee Required)",
        "description": "Congratulations! You have been shortlisted for Software Developer Internship. No technical interview needed. Guaranteed placement with high salary package upon completion. To reserve your internship seat and obtain company software license keys and certification materials, candidate must deposit mandatory onboarding fee of ₹9,999. Send payment screenshot to hr.tcsrecruitment@gmail.com. Limited seats available, act now!",
        "is_fraudulent": 1
    },
    {
        "title": "Cryptocurrency Investment Processing Assistant",
        "description": "Looking for account handlers to process cryptocurrency transactions and transfer USDT. Earn 10% commission on every transaction processed through your personal account. No previous experience needed. We transfer funds to your account, you convert to Bitcoin and transfer to specified wallets. Daily payouts guaranteed. Contact via Telegram only.",
        "is_fraudulent": 1
    },
    {
        "title": "Home Based Typist / Form Filling Job",
        "description": "Huge requirement for home-based typing specialists. Earn ₹25,000 per week for typing 20 pages per day. Zero accuracy errors required. Mandatory registration charge of ₹1,500 for question paper and security deposit. Contact on WhatsApp only. Failure to pay fee will forfeit candidate registration.",
        "is_fraudulent": 1
    },
    {
        "title": "Mystery Shopper / Payment Evaluator",
        "description": "Secret shopper position. We will mail you an advance cashier's check. Deposit check in your bank, withdraw cash, purchase Vanilla Visa gift cards or Apple gift cards, and scratch off the back codes to email pictures of cards to hr_recruiter@yahoo.com to test store cashier efficiency. Keep $400 commission.",
        "is_fraudulent": 1
    }
]


def load_dataset(csv_path: Optional[Path] = None) -> Tuple[List[str], List[int]]:
    """
    Loads text samples and labels from a custom CSV or falls back to synthetic dataset.
    Returns texts (tuple of combined title + description) and labels (0 = Legitimate, 1 = Fraudulent).
    """
    if csv_path and Path(csv_path).exists():
        df = pd.read_csv(csv_path)
        # Expected column names or aliases
        title_col = next((c for c in df.columns if c.lower() in ['title', 'job_title']), None)
        desc_col = next((c for c in df.columns if c.lower() in ['description', 'job_description', 'text']), None)
        label_col = next((c for c in df.columns if c.lower() in ['is_fraudulent', 'fraudulent', 'label', 'target']), None)
        
        if desc_col and label_col:
            texts = []
            for _, row in df.iterrows():
                t = str(row[title_col]) if title_col and pd.notna(row[title_col]) else ""
                d = str(row[desc_col]) if pd.notna(row[desc_col]) else ""
                texts.append(f"{t} {d}".strip())
            labels = df[label_col].astype(int).tolist()
            return texts, labels

    # Fallback to embedded synthetic dataset
    texts = [f"{item['title']} {item['description']}".strip() for item in SYNTHETIC_DATASET]
    labels = [item['is_fraudulent'] for item in SYNTHETIC_DATASET]
    return texts, labels
