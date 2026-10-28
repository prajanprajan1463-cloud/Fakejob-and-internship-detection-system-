from ml.detector import (
    detect_suspicious_indicators,
    detect_positive_indicators,
    get_recommended_actions
)
from ml.text_preprocessor import clean_text, extract_emails, extract_urls


def test_clean_text_normalizer():
    """Verify HTML tag stripping, unicode normalization, and whitespace cleanup."""
    raw = "<p>Urgent hiring&nbsp;for <b>Data Entry</b>!   \n\n\nContact us now.</p>"
    cleaned = clean_text(raw)
    assert "<p>" not in cleaned
    assert "<b>" not in cleaned
    assert "Urgent hiring for Data Entry!" in cleaned
    assert "Contact us now." in cleaned


def test_upfront_fee_detection():
    """Test detection of registration and training fee solicitations."""
    text = "Candidate must pay a refundable registration fee of $150 before joining."
    indicators = detect_suspicious_indicators(text)
    indicator_ids = [i['id'] for i in indicators]
    assert 'UPFRONT_FEE_DEMAND' in indicator_ids
    
    fee_ind = next(i for i in indicators if i['id'] == 'UPFRONT_FEE_DEMAND')
    assert fee_ind['severity'] == 'high'
    assert len(fee_ind['evidence']) > 0


def test_banking_credentials_detection():
    """Test detection of requests for bank passwords, OTP, or CVV."""
    text = "Please share your net banking login and one time password OTP for payroll verification."
    indicators = detect_suspicious_indicators(text)
    indicator_ids = [i['id'] for i in indicators]
    assert 'BANKING_CREDENTIALS' in indicator_ids


def test_equipment_check_scam_detection():
    """Test detection of cashier check overpayment scam pattern."""
    text = "We will send you a check for $4,000 to deposit. Wire the balance to our approved vendor for equipment."
    indicators = detect_suspicious_indicators(text)
    indicator_ids = [i['id'] for i in indicators]
    assert 'EQUIPMENT_CHECK_SCAM' in indicator_ids


def test_chat_app_recruitment_detection():
    """Test detection of recruiter directing candidate to Telegram or WhatsApp only."""
    text = "For immediate interview and task instructions, contact our HR manager on Telegram @quick_job_hr."
    indicators = detect_suspicious_indicators(text)
    indicator_ids = [i['id'] for i in indicators]
    assert 'UNOFFICIAL_COMMUNICATION' in indicator_ids


def test_free_webmail_detection():
    """Test detection of enterprise recruiter using public Gmail / Yahoo email."""
    text = "Send your resume and ID card to hr.microsoftrecruitment@gmail.com for appointment letter."
    indicators = detect_suspicious_indicators(text)
    indicator_ids = [i['id'] for i in indicators]
    assert 'FREE_WEBMAIL_DOMAIN' in indicator_ids


def test_positive_indicators_detection():
    """Test identification of legitimate corporate indicators."""
    text = (
        "We are looking for a Software Engineer. Responsibilities include designing APIs, writing unit tests, "
        "and optimizing SQL queries. Qualifications: Bachelor's degree and 3 years experience. "
        "Equal opportunity employer. Benefits include health insurance, 401k matching, and paid leave. "
        "Contact: careers@technologies-inc.com"
    )
    positives = detect_positive_indicators(
        text=text,
        interview_mode='video',
        company_url='https://technologies-inc.com'
    )
    titles = [p['title'] for p in positives]
    assert any('Structured Job Scope' in t for t in titles)
    assert any('Live Interview' in t for t in titles)
    assert any('Corporate Domain' in t for t in titles)


def test_recommended_actions_generation():
    """Test recommendation generation according to detected flags."""
    indicators = [
        {'id': 'UPFRONT_FEE_DEMAND', 'severity': 'high'},
        {'id': 'UNOFFICIAL_COMMUNICATION', 'severity': 'medium'}
    ]
    actions = get_recommended_actions(75.0, indicators)
    assert any('DO NOT send any money' in a for a in actions)
    assert any('official corporate email' in a for a in actions)
    assert any('extreme caution' in a.lower() for a in actions)

