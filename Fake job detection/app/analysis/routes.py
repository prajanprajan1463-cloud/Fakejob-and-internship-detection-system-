from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import JobAnalysis
from app.analysis import analysis_bp
from app.analysis.forms import JobAnalysisForm
from app.services.analyzer_service import JobAnalyzerService


@analysis_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard displaying personal analysis metrics and risk chart."""
    thresh_low = current_app.config.get('RISK_THRESHOLD_LOW', 30)
    thresh_high = current_app.config.get('RISK_THRESHOLD_HIGH', 60)

    user_analyses = current_user.analyses
    total_count = user_analyses.count()
    
    # Risk breakdowns from user's own database records
    high_count = user_analyses.filter(JobAnalysis.risk_score >= thresh_high).count()
    medium_count = user_analyses.filter(
        JobAnalysis.risk_score >= thresh_low,
        JobAnalysis.risk_score < thresh_high
    ).count()
    low_count = user_analyses.filter(JobAnalysis.risk_score < thresh_low).count()

    # Recent 5 analyses
    recent_analyses = user_analyses.order_by(JobAnalysis.created_at.desc()).limit(5).all()

    return render_template(
        'analysis/dashboard.html',
        total_count=total_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        recent_analyses=recent_analyses,
        thresh_low=thresh_low,
        thresh_high=thresh_high
    )


@analysis_bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    """Form to submit a job or internship posting for risk analysis."""
    form = JobAnalysisForm()
    if form.validate_on_submit():
        try:
            analysis = JobAnalyzerService.analyze_and_record(
                user_id=current_user.id,
                job_title=form.job_title.data,
                company_name=form.company_name.data,
                job_description=form.job_description.data,
                job_location=form.job_location.data,
                employment_type=form.employment_type.data,
                salary_info=form.salary_info.data,
                company_url=form.company_url.data,
                requests_payment=form.requests_payment.data,
                requests_sensitive_info=form.requests_sensitive_info.data,
                interview_mode=form.interview_mode.data,
                additional_notes=form.additional_notes.data
            )
            flash('Job analysis completed successfully.', 'success')
            return redirect(url_for('analysis.result', analysis_id=analysis.id))
        except Exception as e:
            current_app.logger.error(f"Error during job analysis: {e}")
            flash('An unexpected error occurred while analyzing the posting. Please try again.', 'danger')

    return render_template('analysis/analyze.html', form=form)


@analysis_bp.route('/result/<int:analysis_id>')
@login_required
def result(analysis_id):
    """Detailed report view for a specific analysis."""
    analysis = db.session.get(JobAnalysis, analysis_id)
    if not analysis:
        abort(404)

    # Enforce strict server-side ownership / access control
    if analysis.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    thresh_low = current_app.config.get('RISK_THRESHOLD_LOW', 30)
    thresh_high = current_app.config.get('RISK_THRESHOLD_HIGH', 60)

    return render_template(
        'analysis/result.html',
        analysis=analysis,
        thresh_low=thresh_low,
        thresh_high=thresh_high
    )


@analysis_bp.route('/history')
@login_required
def history():
    """Searchable, filterable, paginated history of user's own analyses."""
    thresh_low = current_app.config.get('RISK_THRESHOLD_LOW', 30)
    thresh_high = current_app.config.get('RISK_THRESHOLD_HIGH', 60)

    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    risk_filter = request.args.get('level', '').strip().lower()

    # Base query restricted to current user
    query = JobAnalysis.query.filter_by(user_id=current_user.id)

    # Filter by search terms (title or company)
    if search_query:
        like_term = f"%{search_query}%"
        query = query.filter(
            db.or_(
                JobAnalysis.job_title.ilike(like_term),
                JobAnalysis.company_name.ilike(like_term)
            )
        )

    # Filter by risk level
    if risk_filter == 'high':
        query = query.filter(JobAnalysis.risk_score >= thresh_high)
    elif risk_filter == 'medium':
        query = query.filter(JobAnalysis.risk_score >= thresh_low, JobAnalysis.risk_score < thresh_high)
    elif risk_filter == 'low':
        query = query.filter(JobAnalysis.risk_score < thresh_low)

    pagination = query.order_by(JobAnalysis.created_at.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    return render_template(
        'analysis/history.html',
        pagination=pagination,
        search_query=search_query,
        risk_filter=risk_filter,
        thresh_low=thresh_low,
        thresh_high=thresh_high
    )


@analysis_bp.route('/delete/<int:analysis_id>', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    """Deletes an analysis record belonging to the current user."""
    analysis = db.session.get(JobAnalysis, analysis_id)
    if not analysis:
        abort(404)

    # Authorization check
    if analysis.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    db.session.delete(analysis)
    db.session.commit()
    flash('Analysis record has been deleted.', 'info')
    return redirect(url_for('analysis.history'))

