import re
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError


def validate_url_format(form, field):
    if field.data:
        val = field.data.strip()
        if not re.match(r'^https?://', val, re.IGNORECASE):
            raise ValidationError('URL must start with http:// or https://')
        if len(val) > 500:
            raise ValidationError('URL is too long (maximum 500 characters).')


class JobAnalysisForm(FlaskForm):
    job_title = StringField(
        'Job or Internship Title',
        validators=[
            DataRequired(message='Job title is required.'),
            Length(min=2, max=200, message='Job title must be between 2 and 200 characters.')
        ]
    )
    company_name = StringField(
        'Company or Organization Name',
        validators=[
            DataRequired(message='Company name is required.'),
            Length(min=2, max=200, message='Company name must be between 2 and 200 characters.')
        ]
    )
    job_location = StringField(
        'Job Location',
        validators=[
            Optional(),
            Length(max=150, message='Location must be under 150 characters.')
        ]
    )
    employment_type = SelectField(
        'Employment Type',
        choices=[
            ('', '-- Select Employment Type (Optional) --'),
            ('full_time', 'Full-time'),
            ('part_time', 'Part-time'),
            ('internship', 'Internship'),
            ('contract', 'Contract / Temporary'),
            ('remote', 'Remote / Work from Home')
        ],
        default=''
    )
    salary_info = StringField(
        'Salary / Stipend Information',
        validators=[
            Optional(),
            Length(max=150, message='Salary info must be under 150 characters.')
        ]
    )
    company_url = StringField(
        'Company Website or Job Posting URL',
        validators=[
            Optional(),
            validate_url_format
        ]
    )
    job_description = TextAreaField(
        'Job Description / Posting Text',
        validators=[
            DataRequired(message='Please provide the job description or communication text to analyze.'),
            Length(min=20, max=15000, message='Job text must be between 20 and 15,000 characters.')
        ]
    )
    
    # Red Flag Checkboxes
    requests_payment = BooleanField(
        'Employer asked for money, registration charges, laptop deposit, or training fees.'
    )
    requests_sensitive_info = BooleanField(
        'Employer asked for OTPs, online banking passwords, debit card PIN, or CVV.'
    )
    
    # Interview Process
    interview_mode = SelectField(
        'Interview / Selection Format',
        choices=[
            ('video', 'Live Video Call (Zoom, Teams, Google Meet)'),
            ('in_person', 'In-Person (Office / Campus Interview)'),
            ('formal_phone', 'Formal Phone Call with HR / Hiring Manager'),
            ('chat_only', 'Chat / Text Only (Telegram, WhatsApp, Signal)'),
            ('none', 'No Interview Conducted / Instant Offer Received')
        ],
        default='video'
    )
    
    additional_notes = TextAreaField(
        'Additional Context or Observations',
        validators=[
            Optional(),
            Length(max=2000, message='Notes must be under 2,000 characters.')
        ]
    )

    submit = SubmitField('Analyze Job Posting')

