import os
import pytest
from app import create_app
from app.extensions import db
from app.models import User, JobAnalysis


@pytest.fixture
def app():
    """Create and configure a testing Flask application instance."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for unauthenticated requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner for testing Flask commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Creates a standard test user."""
    user = User(
        full_name='Test Candidate',
        email='candidate@example.com',
        role='user'
    )
    user.set_password('CandidatePass123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def test_admin(app):
    """Creates an administrator test user."""
    admin = User(
        full_name='Test Admin',
        email='admin@example.com',
        role='admin'
    )
    admin.set_password('AdminPass123')
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def authenticated_client(client, test_user):
    """Client logged in as a normal user."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True
    return client


@pytest.fixture
def admin_client(client, test_admin):
    """Client logged in as an administrator."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_admin.id)
        sess['_fresh'] = True
    return client

