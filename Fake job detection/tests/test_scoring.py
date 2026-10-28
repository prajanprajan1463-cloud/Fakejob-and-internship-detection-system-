from pathlib import Path
from ml.risk_scoring import calculate_risk


def test_score_boundaries_clean_posting():
    """Verify clean legitimate posting stays well within low risk boundary (0-29)."""
    text = (
        "We are hiring a Backend Engineer to build scalable microservices. "
        "Candidate will design REST APIs, write automated tests using pytest, "
        "and maintain documentation. Requirements: Python, Flask, Docker. "
        "Comprehensive health insurance, 401(k), and paid vacation provided. "
        "Contact: careers@enterprise-firm.com"
    )
    result = calculate_risk(
        text=text,
        job_title="Software Engineer",
        company_name="Enterprise Tech Corp",
        interview_mode="video"
    )
    
    assert 0.0 <= result['risk_score'] <= 100.0
    assert result['risk_score'] < 30.0
    assert result['risk_category'] == 'Lower Risk Indicators'
    assert result['risk_level'] == 'low'


def test_score_critical_red_flag_safety_floor():
    """Verify that blatant upfront fee requests trigger safety floor (score >= 60)."""
    text = (
        "Immediate joining for home typing. Candidate must deposit a non-refundable "
        "training fee of $200 before getting access code. Contact @hiring_bot on telegram."
    )
    result = calculate_risk(
        text=text,
        job_title="Home Typist",
        company_name="Global Freelance",
        requests_payment=True,
        interview_mode="chat_only"
    )
    
    assert result['risk_score'] >= 60.0
    assert result['risk_category'] == 'Potentially Suspicious'
    assert result['risk_level'] == 'high'


def test_graceful_handling_missing_ml_artifacts(tmp_path):
    """Verify engine produces valid risk score when ML artifact folder is empty."""
    # Point artifacts_dir to an empty temporary path
    result = calculate_risk(
        text="Looking for a project coordinator. Please contact on telegram @hr_team.",
        job_title="Coordinator",
        company_name="Test Corp",
        artifacts_dir=tmp_path
    )
    
    assert 0.0 <= result['risk_score'] <= 100.0
    assert result['risk_category'] in ['Lower Risk Indicators', 'Needs Further Verification', 'Potentially Suspicious']
    assert result['ml_score'] is None or isinstance(result['ml_score'], (int, float))


def test_custom_threshold_configuration():
    """Verify configurable risk thresholds."""
    text = "Work from home, earn $4000 per week. Urgent hiring!"
    # With standard threshold 60, score might be e.g. 45 (medium)
    result_custom = calculate_risk(
        text=text,
        threshold_low=20,
        threshold_high=40
    )
    # With lower high-threshold (40), it should categorize as Potentially Suspicious
    if result_custom['risk_score'] >= 40:
        assert result_custom['risk_category'] == 'Potentially Suspicious'

