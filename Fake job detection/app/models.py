import json
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    analyses = db.relationship('JobAnalysis', backref='author', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class JobAnalysis(db.Model):
    __tablename__ = 'job_analyses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Input details
    job_title = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    job_location = db.Column(db.String(150), nullable=True)
    employment_type = db.Column(db.String(50), nullable=True)
    salary_info = db.Column(db.String(150), nullable=True)
    company_url = db.Column(db.String(500), nullable=True)
    job_description = db.Column(db.Text, nullable=False)
    
    # User-provided structural check flags
    requests_payment = db.Column(db.Boolean, default=False, nullable=False)
    requests_sensitive_info = db.Column(db.Boolean, default=False, nullable=False)
    interview_mode = db.Column(db.String(50), nullable=True)
    additional_notes = db.Column(db.Text, nullable=True)

    # Risk assessment results
    risk_score = db.Column(db.Float, nullable=False)  # 0.0 to 100.0
    risk_category = db.Column(db.String(50), nullable=False)  # 'Lower Risk Indicators', 'Needs Further Verification', 'Potentially Suspicious'
    ml_confidence = db.Column(db.Float, nullable=True)
    
    # Stored structured results (JSON-serialized strings for maximum database portability)
    _detected_indicators = db.Column('detected_indicators', db.Text, default='[]')
    _positive_indicators = db.Column('positive_indicators', db.Text, default='[]')
    _recommended_actions = db.Column('recommended_actions', db.Text, default='[]')
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    @property
    def detected_indicators(self):
        try:
            return json.loads(self._detected_indicators or '[]')
        except Exception:
            return []

    @detected_indicators.setter
    def detected_indicators(self, value):
        self._detected_indicators = json.dumps(value if value is not None else [])

    @property
    def positive_indicators(self):
        try:
            return json.loads(self._positive_indicators or '[]')
        except Exception:
            return []

    @positive_indicators.setter
    def positive_indicators(self, value):
        self._positive_indicators = json.dumps(value if value is not None else [])

    @property
    def recommended_actions(self):
        try:
            return json.loads(self._recommended_actions or '[]')
        except Exception:
            return []

    @recommended_actions.setter
    def recommended_actions(self, value):
        self._recommended_actions = json.dumps(value if value is not None else [])

    def __repr__(self):
        return f"<JobAnalysis id={self.id} title='{self.job_title}' score={self.risk_score}>"


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None

