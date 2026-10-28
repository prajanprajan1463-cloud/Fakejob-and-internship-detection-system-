from functools import wraps
from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, JobAnalysis
from app.admin import admin_bp


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin overview with system metrics and risk distribution."""
    thresh_low = current_app.config.get('RISK_THRESHOLD_LOW', 30)
    thresh_high = current_app.config.get('RISK_THRESHOLD_HIGH', 60)

    total_users = User.query.count()
    total_analyses = JobAnalysis.query.count()

    high_risk_count = JobAnalysis.query.filter(JobAnalysis.risk_score >= thresh_high).count()
    medium_risk_count = JobAnalysis.query.filter(
        JobAnalysis.risk_score >= thresh_low,
        JobAnalysis.risk_score < thresh_high
    ).count()
    low_risk_count = JobAnalysis.query.filter(JobAnalysis.risk_score < thresh_low).count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_analyses = JobAnalysis.query.order_by(JobAnalysis.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_analyses=total_analyses,
        high_risk_count=high_risk_count,
        medium_risk_count=medium_risk_count,
        low_risk_count=low_risk_count,
        recent_users=recent_users,
        recent_analyses=recent_analyses,
        thresh_low=thresh_low,
        thresh_high=thresh_high
    )


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management view with search and pagination."""
    page = request.args.get('page', 1, type=int)
    search_q = request.args.get('q', '').strip()

    query = User.query
    if search_q:
        term = f"%{search_q}%"
        query = query.filter(db.or_(User.full_name.ilike(term), User.email.ilike(term)))

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=15,
        error_out=False
    )

    return render_template('admin/users.html', pagination=pagination, search_q=search_q)


@admin_bp.route('/users/<int:user_id>/toggle-role', methods=['POST'])
@login_required
@admin_required
def toggle_user_role(user_id):
    """Toggles role between 'user' and 'admin'."""
    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    if user.id == current_user.id:
        flash("You cannot change your own administrator role.", "warning")
        return redirect(url_for('admin.users'))

    user.role = 'user' if user.role == 'admin' else 'admin'
    db.session.commit()
    flash(f"Updated role for {user.email} to '{user.role}'.", "success")
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Deletes a user account and associated analyses."""
    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    if user.id == current_user.id:
        flash("You cannot delete your own account from the admin dashboard.", "danger")
        return redirect(url_for('admin.users'))

    email = user.email
    db.session.delete(user)
    db.session.commit()
    flash(f"User account {email} and all associated data have been deleted.", "info")
    return redirect(url_for('admin.users'))


@admin_bp.route('/analyses')
@login_required
@admin_required
def analyses():
    """System-wide analyses management view."""
    thresh_low = current_app.config.get('RISK_THRESHOLD_LOW', 30)
    thresh_high = current_app.config.get('RISK_THRESHOLD_HIGH', 60)

    page = request.args.get('page', 1, type=int)
    search_q = request.args.get('q', '').strip()
    level_filter = request.args.get('level', '').strip().lower()

    query = JobAnalysis.query
    if search_q:
        term = f"%{search_q}%"
        query = query.filter(
            db.or_(JobAnalysis.job_title.ilike(term), JobAnalysis.company_name.ilike(term))
        )

    if level_filter == 'high':
        query = query.filter(JobAnalysis.risk_score >= thresh_high)
    elif level_filter == 'medium':
        query = query.filter(JobAnalysis.risk_score >= thresh_low, JobAnalysis.risk_score < thresh_high)
    elif level_filter == 'low':
        query = query.filter(JobAnalysis.risk_score < thresh_low)

    pagination = query.order_by(JobAnalysis.created_at.desc()).paginate(
        page=page,
        per_page=15,
        error_out=False
    )

    return render_template(
        'admin/analyses.html',
        pagination=pagination,
        search_q=search_q,
        level_filter=level_filter,
        thresh_low=thresh_low,
        thresh_high=thresh_high
    )

