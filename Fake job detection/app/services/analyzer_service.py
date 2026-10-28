from typing import Dict, Any, Optional
from flask import current_app
from app.extensions import db
from app.models import JobAnalysis
from ml.risk_scoring import calculate_risk
from ml.text_preprocessor import clean_text


class JobAnalyzerService:
    @staticmethod
    def analyze_and_record(
        user_id: int,
        job_title: str,
        company_name: str,
        job_description: str,
        job_location: Optional[str] = None,
        employment_type: Optional[str] = None,
        salary_info: Optional[str] = None,
        company_url: Optional[str] = None,
        requests_payment: bool = False,
        requests_sensitive_info: bool = False,
        interview_mode: Optional[str] = None,
        additional_notes: Optional[str] = None
    ) -> JobAnalysis:
        """
        Cleans text, runs heuristic rules and ML classifier,
        persists the assessment in the database, and returns the JobAnalysis record.
        """
        cleaned_desc = clean_text(job_description)
        cleaned_title = clean_text(job_title)
        cleaned_company = clean_text(company_name)

        thresh_low = current_app.config.get('RISK_THRESHOLD_LOW', 30)
        thresh_high = current_app.config.get('RISK_THRESHOLD_HIGH', 60)
        artifacts_dir = current_app.config.get('ML_MODEL_DIR')

        # Run multi-factor detection & risk engine
        assessment: Dict[str, Any] = calculate_risk(
            text=cleaned_desc,
            job_title=cleaned_title,
            company_name=cleaned_company,
            job_location=job_location or "",
            employment_type=employment_type or "",
            salary_info=salary_info or "",
            company_url=company_url or "",
            requests_payment=requests_payment,
            requests_sensitive_info=requests_sensitive_info,
            interview_mode=interview_mode or "",
            threshold_low=thresh_low,
            threshold_high=thresh_high,
            artifacts_dir=artifacts_dir
        )

        analysis = JobAnalysis(
            user_id=user_id,
            job_title=cleaned_title,
            company_name=cleaned_company,
            job_location=job_location.strip() if job_location else None,
            employment_type=employment_type.strip() if employment_type else None,
            salary_info=salary_info.strip() if salary_info else None,
            company_url=company_url.strip() if company_url else None,
            job_description=cleaned_desc,
            requests_payment=requests_payment,
            requests_sensitive_info=requests_sensitive_info,
            interview_mode=interview_mode,
            additional_notes=additional_notes.strip() if additional_notes else None,
            risk_score=assessment['risk_score'],
            risk_category=assessment['risk_category'],
            ml_confidence=assessment.get('ml_confidence')
        )

        # Store JSON structured details
        analysis.detected_indicators = assessment['detected_indicators']
        analysis.positive_indicators = assessment['positive_indicators']
        analysis.recommended_actions = assessment['recommended_actions']

        db.session.add(analysis)
        db.session.commit()

        return analysis

