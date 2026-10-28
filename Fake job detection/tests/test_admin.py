from app.models import User, JobAnalysis
from app.extensions import db


def test_admin_route_protection_unauthenticated(client):
    """Test guest cannot access admin dashboard."""
    response = client.get('/admin/')
    assert response.status_code == 302


def test_admin_route_protection_normal_user(authenticated_client):
    """Test standard user receives 403 Forbidden when accessing admin area."""
    response = authenticated_client.get('/admin/')
    assert response.status_code == 403

    response_users = authenticated_client.get('/admin/users')
    assert response_users.status_code == 403


def test_admin_dashboard_access(admin_client):
    """Test administrator can access dashboard and view metrics."""
    response = admin_client.get('/admin/')
    assert response.status_code == 200
    assert b'System Administration Console' in response.data
    assert b'Global Threat Distribution' in response.data


def test_admin_cannot_toggle_self(admin_client, test_admin):
    """Test admin cannot demote themselves."""
    response = admin_client.post(f'/admin/users/{test_admin.id}/toggle-role', follow_redirects=True)
    assert response.status_code == 200
    assert b'cannot change your own administrator role' in response.data
    assert test_admin.is_admin is True


def test_admin_toggle_other_user_role(admin_client, test_user, app):
    """Test admin can promote a standard user to admin and demote back."""
    # Promote
    response = admin_client.post(f'/admin/users/{test_user.id}/toggle-role', follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        u = db.session.get(User, test_user.id)
        assert u.role == 'admin'

    # Demote back
    response2 = admin_client.post(f'/admin/users/{test_user.id}/toggle-role', follow_redirects=True)
    assert response2.status_code == 200
    with app.app_context():
        u2 = db.session.get(User, test_user.id)
        assert u2.role == 'user'


def test_admin_delete_user(admin_client, app):
    """Test admin can delete another user account."""
    with app.app_context():
        user = User(full_name='Target User', email='target@example.com', role='user')
        user.set_password('Pass1234')
        db.session.add(user)
        db.session.commit()
        u_id = user.id

    response = admin_client.post(f'/admin/users/{u_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'have been deleted' in response.data

    with app.app_context():
        assert db.session.get(User, u_id) is None

