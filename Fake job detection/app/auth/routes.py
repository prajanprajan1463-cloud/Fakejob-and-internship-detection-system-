from urllib.parse import urlsplit
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User
from app.auth.forms import (
    RegistrationForm,
    LoginForm,
    UpdateProfileForm,
    ChangePasswordForm,
    DeleteAccountForm
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def is_safe_url(target: str) -> bool:
    """Validates that a redirect target URL is safe and points to the same host."""
    if not target:
        return False
    ref_url = urlsplit(request.host_url)
    test_url = urlsplit(target)
    return test_url.scheme in ('', 'http', 'https') and ref_url.netloc == test_url.netloc or not test_url.netloc


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('analysis.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            role='user'
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been successfully created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during registration: {e}")
            flash('An unexpected error occurred while creating your account. Please try again.', 'danger')

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('analysis.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email.ilike(form.email.data.strip().lower())).first()
        
        # Protect against user enumeration / timing by running check_password regardless
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.full_name.split()[0]}!", 'success')
            
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('analysis.dashboard'))
        else:
            flash('Invalid email address or password. Please verify your credentials.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = UpdateProfileForm(prefix='profile', full_name=current_user.full_name)
    password_form = ChangePasswordForm(prefix='password')
    delete_form = DeleteAccountForm(prefix='delete')

    # Handle Name Update
    if profile_form.submit.data and profile_form.validate_on_submit():
        current_user.full_name = profile_form.full_name.data.strip()
        db.session.commit()
        flash('Your profile name has been updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    # Handle Password Change
    if password_form.submit.data and password_form.validate_on_submit():
        if not current_user.check_password(password_form.current_password.data):
            flash('Current password is incorrect.', 'danger')
        else:
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('auth.profile'))

    # Handle Account Deletion
    if delete_form.submit.data and delete_form.validate_on_submit():
        if not current_user.check_password(delete_form.current_password.data):
            flash('Incorrect password. Account was not deleted.', 'danger')
        else:
            user_to_delete = current_user._get_current_object()
            logout_user()
            db.session.delete(user_to_delete)
            db.session.commit()
            flash('Your account and all associated analyses have been permanently deleted.', 'info')
            return redirect(url_for('main.index'))

    # Summary metrics for current user
    analyses_count = current_user.analyses.count()
    return render_template(
        'auth/profile.html',
        profile_form=profile_form,
        password_form=password_form,
        delete_form=delete_form,
        analyses_count=analyses_count
    )

