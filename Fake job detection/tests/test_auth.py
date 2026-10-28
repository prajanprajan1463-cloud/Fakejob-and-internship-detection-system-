from app.models import User
from app.extensions import db


def test_user_registration(client, app):
    """Test successful user registration."""
    response = client.post('/auth/register', data={
        'full_name': 'New Student',
        'email': 'student@example.com',
        'password': 'Password123',
        'confirm_password': 'Password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Your account has been successfully created' in response.data
    
    with app.app_context():
        user = User.query.filter_by(email='student@example.com').first()
        assert user is not None
        assert user.full_name == 'New Student'
        assert user.role == 'user'
        assert user.password_hash != 'Password123'  # Verify hashed


def test_duplicate_email_rejection(client, test_user):
    """Test that duplicate email registration is rejected."""
    response = client.post('/auth/register', data={
        'full_name': 'Duplicate User',
        'email': test_user.email,  # already exists
        'password': 'Password123',
        'confirm_password': 'Password123'
    })
    
    assert response.status_code == 200
    assert b'already exists' in response.data


def test_password_policy_enforcement(client):
    """Test rejection of short passwords and passwords missing digits."""
    # Too short
    resp_short = client.post('/auth/register', data={
        'full_name': 'User Short',
        'email': 'short@example.com',
        'password': 'pass1',
        'confirm_password': 'pass1'
    })
    assert b'at least 8 characters' in resp_short.data

    # No number
    resp_no_num = client.post('/auth/register', data={
        'full_name': 'User NoNum',
        'email': 'nonum@example.com',
        'password': 'passwordonly',
        'confirm_password': 'passwordonly'
    })
    assert b'contain both letters and at least one number' in resp_no_num.data


def test_successful_login(client, test_user):
    """Test successful user login."""
    response = client.post('/auth/login', data={
        'email': 'candidate@example.com',
        'password': 'CandidatePass123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome back' in response.data
    assert b'Dashboard' in response.data


def test_failed_login_invalid_password(client, test_user):
    """Test login failure with wrong password."""
    response = client.post('/auth/login', data={
        'email': 'candidate@example.com',
        'password': 'WrongPassword123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid email address or password' in response.data


def test_failed_login_nonexistent_email(client):
    """Test login failure with unverified email."""
    response = client.post('/auth/login', data={
        'email': 'nobody@example.com',
        'password': 'Password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid email address or password' in response.data


def test_logout(authenticated_client):
    """Test user logout."""
    response = authenticated_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out' in response.data


def test_protected_routes_redirect_unauthenticated(client):
    """Test that authenticated views redirect guests to login."""
    routes = [
        '/analysis/dashboard',
        '/analysis/analyze',
        '/analysis/history',
        '/auth/profile'
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']

