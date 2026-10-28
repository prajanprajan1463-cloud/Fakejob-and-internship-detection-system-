import re
from typing import Dict, List, Any
from ml.text_preprocessor import extract_emails, extract_urls


# Public free email providers often misused by impersonators
PUBLIC_EMAIL_DOMAINS = {
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
    'aol.com', 'mail.com', 'protonmail.com', 'yandex.com', 'zoho.com', 'icloud.com'
}

# Rule definitions with compiled patterns, severity, weights, and educational explanations
RULES = [
    {
        'id': 'UPFRONT_FEE_DEMAND',
        'title': 'Request for Upfront Payment or Fees',
        'severity': 'high',
        'weight': 35.0,
        'explanation': (
            'Legitimate employers and reputable recruitment agencies do not ask candidates to pay '
            'registration fees, training deposits, visa processing charges, or laptop security fees before hiring.'
        ),
        'patterns': [
            re.compile(r'\b(?:registration|training|application|processing|security|documentation|onboarding)\s+(?:fee|fees|charge|charges|deposit|amount|cost)\b', re.IGNORECASE),
            re.compile(r'\b(?:pay|deposit|transfer|send)\s+(?:money|cash|advance|fee|\$|₹|rs\.?|usd)\b', re.IGNORECASE),
            re.compile(r'\b(?:refundable|non-refundable)\s+(?:deposit|fee|charge|security)\b', re.IGNORECASE),
            re.compile(r'\bpurchase\s+(?:your\s+own\s+)?(?:starter\s+kit|software\s+license|materials)\b', re.IGNORECASE),
        ]
    },
    {
        'id': 'BANKING_CREDENTIALS',
        'title': 'Request for Sensitive Financial or Identity Credentials',
        'severity': 'high',
        'weight': 35.0,
        'explanation': (
            'Employers only need bank account routing details for payroll after an official contract is signed. '
            'Never provide online banking passwords, debit card PINs, CVVs, or OTPs during job screening.'
        ),
        'patterns': [
            re.compile(r'\b(?:otp|one[- ]time[- ]password|cvv|pin\s+number|internet\s+banking\s+password)\b', re.IGNORECASE),
            re.compile(r'\b(?:share|provide|send)\s+(?:bank\s+login|credit\s+card|debit\s+card\s+details|card\s+number)\b', re.IGNORECASE),
            re.compile(r'\b(?:crypto|bitcoin|usdt|ethereum|gift\s+card|apple\s+gift\s+card|vanilla\s+card)\b', re.IGNORECASE),
            re.compile(r'\b(?:wire\s+transfer|western\s+union|moneygram)\b', re.IGNORECASE),
        ]
    },
    {
        'id': 'EQUIPMENT_CHECK_SCAM',
        'title': 'Overpayment / Equipment Check Scam Pattern',
        'severity': 'high',
        'weight': 30.0,
        'explanation': (
            'A classic fake-check scam: fraudsters send a counterfeit check to deposit, asking you to wire '
            'money to their "approved vendor" for home office equipment. The check bounces days later, leaving you liable.'
        ),
        'patterns': [
            re.compile(r'\b(?:send|mail|issue)\s+(?:you\s+a\s+)?(?:check|cheque)\s+(?:for|to\s+buy|to\s+purchase)\b', re.IGNORECASE),
            re.compile(r'\b(?:certified|authorized|approved)\s+vendor\s+(?:for\s+equipment|to\s+purchase)\b', re.IGNORECASE),
            re.compile(r'\b(?:deposit\s+(?:the\s+)?(?:check|cheque)|cash\s+(?:the\s+)?check)\b', re.IGNORECASE),
            re.compile(r'\bkeep\s+(?:the\s+)?rest\s+(?:for\s+yourself|as\s+your\s+pay)\b', re.IGNORECASE),
        ]
    },
    {
        'id': 'UNOFFICIAL_COMMUNICATION',
        'title': 'Informal / Chat-Only Hiring Communication',
        'severity': 'medium',
        'weight': 20.0,
        'explanation': (
            'Scammers avoid corporate tracking by conducting hiring exclusively over messaging apps '
            'like Telegram, WhatsApp, Signal, or personal chat handles without a verified corporate email or portal.'
        ),
        'patterns': [
            re.compile(r'\b(?:contact|message|dm|ping|reach|chat|apply)\b.{0,40}\b(?:telegram|whatsapp|signal)\b', re.IGNORECASE),
            re.compile(r'\b(?:telegram\s*(?:handle|id|group|channel)?|t\.me/|@\w{4,}\s+on\s+telegram)\b', re.IGNORECASE),
            re.compile(r'\b(?:whatsapp\s*(?:only|interview|chat|number)|message\s+on\s+whatsapp)\b', re.IGNORECASE),
            re.compile(r'\b(?:signal\s+app|google\s+hangouts\s+chat|skype\s+interview\s+only)\b', re.IGNORECASE),
        ]
    },
    {
        'id': 'UNREALISTIC_COMPENSATION',
        'title': 'Disproportionate Salary or Effortless Income Claims',
        'severity': 'medium',
        'weight': 18.0,
        'explanation': (
            'Offers promising unusually high compensation for minimal effort (e.g., $5,000/week or ₹50,000/day '
            'for basic typing, data entry, or liking social media posts) are common lures for advance-fee scams.'
        ),
        'patterns': [
            re.compile(r'\b(?:earn|make)\s+(?:\$|₹|rs\.?)\s*(?:[3-9]\d{2,}|[1-9]\d{3,})\s*(?:per\s+day|daily|per\s+hour|hourly)\b', re.IGNORECASE),
            re.compile(r'\b(?:earn|make)\s+(?:\$|₹|rs\.?)\s*(?:[1-9]\d{4,})\s*(?:per\s+week|weekly)\b', re.IGNORECASE),
            re.compile(r'\b(?:work\s+(?:1|2|3)\s*(?:hours|hrs)\s*(?:a|per)\s*day\s*and\s*earn)\b', re.IGNORECASE),
            re.compile(r'\b(?:unlimited\s+earning\s+potential|get\s+rich\s+quick|daily\s+payouts\s+guaranteed)\b', re.IGNORECASE),
            re.compile(r'\b(?:like\s+videos|subscribe\s+channels|copy\s*[- ]*\s*paste\s*work)\s*(?:to\s*earn|for\s*daily\s*cash)\b', re.IGNORECASE),
        ]
    },
    {
        'id': 'INSTANT_HIRING_NO_EVALUATION',
        'title': 'Instant Offer Without Formal Selection Process',
        'severity': 'medium',
        'weight': 18.0,
        'explanation': (
            'Legitimate companies require at least one structured technical or behavioral interview, '
            'reference checks, and portfolio/resume review before extending a written employment offer.'
        ),
        'patterns': [
            re.compile(r'\b(?:immediate\s+offer|direct\s+selection|no\s+interview\s+required|selected\s+without\s+interview)\b', re.IGNORECASE),
            re.compile(r'\b(?:100%\s*(?:job\s*)?guaranteed|guaranteed\s+(?:placement|job|hiring))\b', re.IGNORECASE),
            re.compile(r'\b(?:congratulations|hired\s+immediately|start\s+today\s+no\s+experience)\b', re.IGNORECASE),
            re.compile(r'\b(?:no\s+resume|no\s+cv|no\s+experience\s+needed\s*,\s*instant\s+joining)\b', re.IGNORECASE),
        ]
    },
    {
        'id': 'URGENCY_TACTICS',
        'title': 'High Pressure Urgency and Artificial Scarcity',
        'severity': 'low',
        'weight': 12.0,
        'explanation': (
            'Scammers create artificial urgency (e.g. "Only 2 spots left", "Offer expires in 2 hours") '
            'to prevent candidates from verifying the company or consulting others.'
        ),
        'patterns': [
            re.compile(r'\b(?:urgent\s+hiring|hurry\s+up|limited\s+slots|limited\s+openings|few\s+seats\s+left)\b', re.IGNORECASE),
            re.compile(r'\b(?:respond\s+within\s+(?:24|12|2)\s+hours|offer\s+expires\s+(?:today|soon|immediately))\b', re.IGNORECASE),
            re.compile(r'\b(?:act\s+fast|first\s+come\s+first\s+serve|grab\s+this\s+opportunity\s+now)\b', re.IGNORECASE),
        ]
    },
    {
        'id': 'VAGUE_JOB_SPECIFICATION',
        'title': 'Excessively Vague Job Description / Generic Duties',
        'severity': 'low',
        'weight': 10.0,
        'explanation': (
            'Legitimate positions clearly outline specific tools, responsibilities, team structures, and '
            'performance expectations rather than relying only on generic catch-all phrases.'
        ),
        'patterns': [
            re.compile(r'\b(?:simple\s+data\s+entry|form\s+filling|ad\s+posting|sms\s+sending\s+job)\b', re.IGNORECASE),
            re.compile(r'\b(?:anybody\s+can\s+do|housewives\s+students|any\s+age\s+can\s+apply)\b', re.IGNORECASE),
        ]
    }
]


def detect_suspicious_indicators(
    text: str,
    job_title: str = "",
    company_name: str = "",
    requests_payment: bool = False,
    requests_sensitive_info: bool = False,
    interview_mode: str = "",
    company_url: str = ""
) -> List[Dict[str, Any]]:
    """
    Analyzes job description and metadata against rule sets and structural inputs.
    Returns a list of detected suspicious indicators with evidence and explanations.
    """
    detected: List[Dict[str, Any]] = []
    combined_text = f"{job_title}\n{company_name}\n{text}".strip()
    
    # 1. Evaluate Rule-based Text Patterns
    for rule in RULES:
        matched_evidence = []
        for pattern in rule['patterns']:
            for match in pattern.finditer(combined_text):
                # Extract snippet around match for context
                start = max(0, match.start() - 30)
                end = min(len(combined_text), match.end() + 30)
                snippet = combined_text[start:end].replace('\n', ' ').strip()
                if snippet not in matched_evidence:
                    matched_evidence.append(snippet)
        
        if matched_evidence:
            detected.append({
                'id': rule['id'],
                'title': rule['title'],
                'severity': rule['severity'],
                'weight': rule['weight'],
                'explanation': rule['explanation'],
                'evidence': matched_evidence[:3]  # Keep top 3 snippets
            })
    
    # 2. Check Structural Input Flags
    # A. Explicit upfront payment request flag
    if requests_payment:
        # Check if already detected from text
        existing = next((item for item in detected if item['id'] == 'UPFRONT_FEE_DEMAND'), None)
        if not existing:
            detected.append({
                'id': 'UPFRONT_FEE_DEMAND',
                'title': 'Request for Upfront Payment or Fees',
                'severity': 'high',
                'weight': 35.0,
                'explanation': 'Candidate reported that the employer asked for an upfront registration, training, or deposit fee.',
                'evidence': ['User indicated employer explicitly requested fees or payment.']
            })
        else:
            if 'User indicated employer explicitly requested fees or payment.' not in existing['evidence']:
                existing['evidence'].append('User confirmed employer requested upfront payment.')

    # B. Explicit sensitive information request flag
    if requests_sensitive_info:
        existing = next((item for item in detected if item['id'] == 'BANKING_CREDENTIALS'), None)
        if not existing:
            detected.append({
                'id': 'BANKING_CREDENTIALS',
                'title': 'Request for Sensitive Financial or Identity Credentials',
                'severity': 'high',
                'weight': 35.0,
                'explanation': 'Candidate reported that the employer requested banking credentials, OTPs, or excessive personal identification.',
                'evidence': ['User indicated employer requested OTP, banking login, or identity cards.']
            })
        else:
            if 'User indicated employer requested OTP, banking login, or identity cards.' not in existing['evidence']:
                existing['evidence'].append('User confirmed employer requested sensitive credentials.')

    # C. Interview Mode checks
    if interview_mode in ['chat_only', 'none', 'instant_offer']:
        existing = next((item for item in detected if item['id'] in ['UNOFFICIAL_COMMUNICATION', 'INSTANT_HIRING_NO_EVALUATION']), None)
        if interview_mode in ['chat_only']:
            detected.append({
                'id': 'CHAT_INTERVIEW_ONLY',
                'title': 'Interview Conducted Exclusively via Chat / Messenger',
                'severity': 'medium',
                'weight': 22.0,
                'explanation': 'Screening was performed solely via text messages (e.g. Telegram or WhatsApp) without audio/video or face-to-face interaction.',
                'evidence': ['Interview conducted exclusively via text/messaging app.']
            })
        elif interview_mode in ['none', 'instant_offer']:
            detected.append({
                'id': 'NO_INTERVIEW_OFFER',
                'title': 'Job Offer Extended Without Any Interview',
                'severity': 'high',
                'weight': 25.0,
                'explanation': 'An offer of employment without any screening conversation is one of the clearest signs of an impersonation or fake job scam.',
                'evidence': ['User reported job offer was made with no interview conducted.']
            })

    # 3. Check Email Domains in description
    emails = extract_emails(combined_text)
    public_emails_found = [e for e in emails if e.split('@')[-1].lower() in PUBLIC_EMAIL_DOMAINS]
    if public_emails_found:
        detected.append({
            'id': 'FREE_WEBMAIL_DOMAIN',
            'title': 'Recruiter Using Free / Public Webmail Address',
            'severity': 'medium',
            'weight': 15.0,
            'explanation': (
                f"Recruitment contact email ({', '.join(public_emails_found[:2])}) uses a free public email provider "
                "(such as Gmail or Yahoo) instead of an official corporate domain name."
            ),
            'evidence': [f"Public email detected: {e}" for e in public_emails_found[:2]]
        })

    # 4. Check Short / Suspicious Description length
    word_count = len(text.split())
    if word_count < 25:
        detected.append({
            'id': 'ABNORMALLY_SHORT_DESCRIPTION',
            'title': 'Extremely Brief or Incomplete Description',
            'severity': 'low',
            'weight': 8.0,
            'explanation': 'The job posting contains fewer than 25 words, lacking the standard requirements, responsibilities, and qualifications typical of real postings.',
            'evidence': [f"Description contains only {word_count} words."]
        })

    return detected


def detect_positive_indicators(
    text: str,
    job_title: str = "",
    company_name: str = "",
    interview_mode: str = "",
    company_url: str = ""
) -> List[Dict[str, str]]:
    """
    Detects legitimate signals and positive employment indicators when supported by data.
    """
    positives: List[Dict[str, str]] = []
    combined_text = f"{job_title}\n{company_name}\n{text}".strip().lower()

    # 1. Standard Professional Interview Conducted
    if interview_mode in ['in_person', 'video', 'formal_phone']:
        positives.append({
            'title': 'Standard Multi-Stage or Live Interview',
            'description': 'The hiring process included live verbal or face-to-face interaction rather than untraceable text messages.'
        })

    # 2. Comprehensive Job Description (> 35 words with structured sections)
    words = len(text.split())
    has_structure = any(h in combined_text for h in ['responsibilities', 'requirements', 'qualifications', 'duties', 'skills required', 'about the role'])
    if words >= 35 and has_structure:
        positives.append({
            'title': 'Structured Job Scope and Qualifications',
            'description': f'Detailed posting ({words} words) explicitly detailing day-to-day responsibilities, prerequisites, and skills.'
        })

    # 3. Transparent Corporate Website Provided
    if company_url and ('http://' in company_url or 'https://' in company_url):
        # Basic check that URL is not a free link shortener
        shorteners = ['bit.ly', 'tinyurl.com', 't.me', 'wa.me', 'cutt.ly', 'is.gd']
        if not any(s in company_url.lower() for s in shorteners):
            positives.append({
                'title': 'Direct Company Web Presence Provided',
                'description': 'A direct company website was submitted for verification and due diligence.'
            })

    # 4. Explicit Anti-Fee Policy or Standard Corporate Benefits
    fee_disclaimer_patterns = [
        r'we never (?:charge|ask for) (?:any )?(?:fees?|money|payment)',
        r'(?:does not charge|no charge) (?:any )?(?:recruitment|application|processing) fees?',
        r'equal opportunity employer',
        r'benefits include (?:health insurance|401k|provident fund|paid time off)'
    ]
    for p in fee_disclaimer_patterns:
        if re.search(p, combined_text):
            positives.append({
                'title': 'Standard Corporate Policy / Benefits Clause',
                'description': 'Posting mentions standard corporate protections, equal opportunity statement, or anti-fee recruitment policies.'
            })
            break

    # 5. Non-public corporate domain detected in email
    emails = extract_emails(text)
    corporate_emails = [e for e in emails if e.split('@')[-1].lower() not in PUBLIC_EMAIL_DOMAINS]
    if corporate_emails:
        positives.append({
            'title': 'Corporate Domain Email Address',
            'description': f"Contact email ({corporate_emails[0]}) uses an organization-specific domain."
        })

    return positives


def get_recommended_actions(risk_score: float, detected_indicators: List[Dict[str, Any]]) -> List[str]:
    """
    Generates actionable, safety-first verification steps based on score and detected indicators.
    """
    actions = []
    indicator_ids = {item['id'] for item in detected_indicators}

    if 'UPFRONT_FEE_DEMAND' in indicator_ids:
        actions.append("DO NOT send any money, deposit, or payment. Legitimate employers never charge candidates for jobs or mandatory training.")
    
    if 'BANKING_CREDENTIALS' in indicator_ids:
        actions.append("NEVER share banking credentials, OTPs, or credit card details. Payroll details are only required after formal employment starts.")

    if 'EQUIPMENT_CHECK_SCAM' in indicator_ids:
        actions.append("Refuse any check sent to purchase equipment through a specific vendor. Bank checks can take weeks to bounce back.")

    if 'UNOFFICIAL_COMMUNICATION' in indicator_ids or 'CHAT_INTERVIEW_ONLY' in indicator_ids:
        actions.append("Request communication through official corporate email and schedule a verified video or in-person interview before proceeding.")

    if 'FREE_WEBMAIL_DOMAIN' in indicator_ids:
        actions.append("Search the organization's official website careers page or LinkedIn to verify if the recruiter is a legitimate employee.")

    # General recommended best practices
    actions.append("Cross-check the job opening directly on the company's official 'Careers' portal.")
    actions.append("Look up independent company reviews and scam reports on platforms like Glassdoor, Indeed, and the Better Business Bureau (BBB).")
    actions.append("Verify the recruiter's identity on LinkedIn and ensure their message came from a verified corporate email.")

    if risk_score >= 60:
        actions.insert(0, "Exercise extreme caution: Multiple strong indicators of employment fraud were detected.")
    elif risk_score >= 30:
        actions.insert(0, "Exercise due diligence: Several ambiguous or cautionary patterns were identified.")

    return actions
