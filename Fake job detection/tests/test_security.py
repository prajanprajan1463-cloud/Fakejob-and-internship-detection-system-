import pytest
from app import create_app
from app.auth.routes import is_safe_url
from app.models import User
from werkzeug.security import check_password_hash


def test_password_hash_strength():
    """Verify passwords are strongly hashed and not stored in plaintext."""
    user = User(full_name="Sec User", email="sec@example.com")
    raw_pass = "ComplexPassword2026"
    user.set_password(raw_pass)

    assert user.password_hash != raw_pass
    assert user.password_hash.startswith("scrypt:") or user.password_hash.startswith("pbkdf2:")
    assert user.check_password(raw_pass) is True
    assert user.check_password("WrongPassword") is False


def test_open_redirect_protection(client, test_user):
    """Test that login redirects ignore external malicious host URLs."""
    # Attempt redirect to malicious external site
    malicious_target = "https://malicious-scam-site.com/steal-creds"
    response = client.post(f'/auth/login?next={malicious_target}', data={
        'email': test_user.email,
        'password': 'CandidatePass123'
    })
    
    # Must redirect to default dashboard, NOT malicious external site
    assert response.status_code == 302
    assert malicious_target not in response.headers['Location']
    assert '/analysis/dashboard' in response.headers['Location']


def test_is_safe_url_logic(app):
    """Test is_safe_url helper for internal vs external URLs."""
    with app.test_request_context('http://127.0.0.1:5000/auth/login'):
        assert is_safe_url('/analysis/dashboard') is True
        assert is_safe_url('/analysis/analyze') is True
        assert is_safe_url('http://127.0.0.1:5000/profile') is True
        assert is_safe_url('https://evil-site.com') is False
        assert is_safe_url('//evil-site.com') is False
        assert is_safe_url('') is False


def test_csrf_protection_when_active():
    """Verify CSRF token requirement when WTF_CSRF_ENABLED is True."""
    # Create app with CSRF enabled
    csrf_app = create_app('development')
    csrf_app.config['WTF_CSRF_ENABLED'] = True
    csrf_app.config['TESTING'] = True
    
    test_client = csrf_app.test_client()
    
    # POST without CSRF token should be rejected with 400
    response = test_client.post('/auth/login', data={
        'email': 'anyone@example.com',
        'password': 'Password123'
    })
    assert response.status_code == 400
    assert b'CSRF' in response.data or b'400' in response.data

