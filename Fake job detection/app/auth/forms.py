import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User


def validate_password_strength(form, field):
    password = field.data or ''
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
        raise ValidationError('Password must contain both letters and at least one number.')


class RegistrationForm(FlaskForm):
    full_name = StringField(
        'Full Name',
        validators=[DataRequired(message='Please enter your full name.'), Length(min=2, max=100)]
    )
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Please enter your email address.'),
            Email(message='Please enter a valid email address.'),
            Length(max=120)
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Please choose a password.'),
            validate_password_strength
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password.'),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        normalized_email = field.data.strip().lower()
        if User.query.filter(User.email.ilike(normalized_email)).first():
            raise ValidationError('An account with this email address already exists. Please log in instead.')


class LoginForm(FlaskForm):
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Please enter your email address.'),
            Email(message='Please enter a valid email address.')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Please enter your password.')]
    )
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign In')


class UpdateProfileForm(FlaskForm):
    full_name = StringField(
        'Full Name',
        validators=[DataRequired(message='Please enter your name.'), Length(min=2, max=100)]
    )
    submit = SubmitField('Update Name')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired(message='Please enter your current password.')]
    )
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message='Please enter your new password.'),
            validate_password_strength
        ]
    )
    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message='Please confirm your new password.'),
            EqualTo('new_password', message='New passwords must match.')
        ]
    )
    submit = SubmitField('Update Password')


class DeleteAccountForm(FlaskForm):
    current_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(message='Please enter your password to confirm deletion.')]
    )
    confirm_phrase = StringField(
        'Type "DELETE" to confirm',
        validators=[DataRequired(message='Please type DELETE to confirm.')]
    )
    submit = SubmitField('Permanently Delete My Account')

    def validate_confirm_phrase(self, field):
        if field.data.strip() != 'DELETE':
            raise ValidationError('You must type the word DELETE exactly to confirm.')

