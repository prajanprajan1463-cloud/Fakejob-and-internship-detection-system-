from app.models import User, JobAnalysis
from app.extensions import db


def test_job_analysis_workflow(authenticated_client, test_user, app):
    """Test full job analysis submission and database recording."""
    response = authenticated_client.post('/analysis/analyze', data={
        'job_title': 'Python Developer Intern',
        'company_name': 'Innovative Labs',
        'job_description': 'We need an intern to build Flask web apps and APIs. Minimum 20 words for this valid job posting to pass length check.',
        'job_location': 'Remote',
        'employment_type': 'internship',
        'salary_info': '$25/hr',
        'company_url': 'https://innovativelabs.io',
        'requests_payment': False,
        'requests_sensitive_info': False,
        'interview_mode': 'video',
        'additional_notes': 'Found on LinkedIn.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Risk Assessment Report' in response.data or b'Innovative Labs' in response.data

    with app.app_context():
        analysis = JobAnalysis.query.filter_by(user_id=test_user.id).first()
        assert analysis is not None
        assert analysis.job_title == 'Python Developer Intern'
        assert 0.0 <= analysis.risk_score <= 100.0
        assert analysis.risk_category in ['Lower Risk Indicators', 'Needs Further Verification', 'Potentially Suspicious']
        assert isinstance(analysis.detected_indicators, list)


def test_analysis_empty_submission_rejected(authenticated_client):
    """Test rejection when required fields are missing."""
    response = authenticated_client.post('/analysis/analyze', data={
        'job_title': '',
        'company_name': '',
        'job_description': ''
    })
    assert response.status_code == 200
    assert b'Job title is required' in response.data
    assert b'Company name is required' in response.data


def test_analysis_invalid_url_rejected(authenticated_client):
    """Test validation rejection for malformed URLs."""
    response = authenticated_client.post('/analysis/analyze', data={
        'job_title': 'Engineer',
        'company_name': 'Tech Corp',
        'job_description': 'Valid long description for this position with more than 20 characters.',
        'company_url': 'javascript:alert(1)'  # Not http/https
    })
    assert response.status_code == 200
    assert b'URL must start with http:// or https://' in response.data


def test_user_data_isolation(client, app, test_user):
    """Test that User A cannot view User B's analysis report (HTTP 403)."""
    # Create User B
    with app.app_context():
        user_b = User(full_name='User B', email='user_b@example.com', role='user')
        user_b.set_password('Pass1234')
        db.session.add(user_b)
        db.session.commit()

        # Create analysis owned by User B
        analysis = JobAnalysis(
            user_id=user_b.id,
            job_title='Secret Role',
            company_name='Secret Corp',
            job_description='Some secret job description text that is long enough.',
            risk_score=25.0,
            risk_category='Lower Risk Indicators'
        )
        db.session.add(analysis)
        db.session.commit()
        analysis_id = analysis.id

    # Log in as test_user (User A)
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True

    # User A attempts to view User B's analysis
    response = client.get(f'/analysis/result/{analysis_id}')
    assert response.status_code == 403


def test_delete_analysis_by_owner(authenticated_client, test_user, app):
    """Test that user can delete their own analysis record."""
    with app.app_context():
        analysis = JobAnalysis(
            user_id=test_user.id,
            job_title='Temporary Job',
            company_name='Temp Corp',
            job_description='Temporary description that is long enough.',
            risk_score=15.0,
            risk_category='Lower Risk Indicators'
        )
        db.session.add(analysis)
        db.session.commit()
        a_id = analysis.id

    response = authenticated_client.post(f'/analysis/delete/{a_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Analysis record has been deleted' in response.data

    with app.app_context():
        deleted = db.session.get(JobAnalysis, a_id)
        assert deleted is None


def test_nonexistent_analysis_404(authenticated_client):
    """Test 404 for non-existent analysis record."""
    response = authenticated_client.get('/analysis/result/99999')
    assert response.status_code == 404

