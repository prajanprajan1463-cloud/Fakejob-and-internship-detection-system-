import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import joblib

from ml.text_preprocessor import prepare_for_vectorizer
from ml.detector import (
    detect_suspicious_indicators,
    detect_positive_indicators,
    get_recommended_actions
)

# Global cache for loaded ML model and vectorizer
_MODEL = None
_VECTORIZER = None
_MODEL_LOADED = False


def load_ml_model(artifacts_dir: Optional[Path] = None):
    """
    Safely loads the trained Scikit-learn model and TF-IDF vectorizer if present.
    Caches loaded artifacts in memory.
    """
    global _MODEL, _VECTORIZER, _MODEL_LOADED
    
    if _MODEL_LOADED:
        return _MODEL, _VECTORIZER
        
    if artifacts_dir is None:
        artifacts_dir = Path(__file__).resolve().parent / 'artifacts'
        
    model_path = artifacts_dir / 'job_classifier.joblib'
    vec_path = artifacts_dir / 'tfidf_vectorizer.joblib'
    
    if model_path.exists() and vec_path.exists():
        try:
            _MODEL = joblib.load(model_path)
            _VECTORIZER = joblib.load(vec_path)
            _MODEL_LOADED = True
        except Exception:
            _MODEL = None
            _VECTORIZER = None
            _MODEL_LOADED = False
    else:
        _MODEL = None
        _VECTORIZER = None
        _MODEL_LOADED = False

    return _MODEL, _VECTORIZER


def calculate_risk(
    text: str,
    job_title: str = "",
    company_name: str = "",
    job_location: str = "",
    employment_type: str = "",
    salary_info: str = "",
    company_url: str = "",
    requests_payment: bool = False,
    requests_sensitive_info: bool = False,
    interview_mode: str = "",
    threshold_low: int = 30,
    threshold_high: int = 60,
    artifacts_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Computes explainable, multi-factor risk score combining heuristic rules,
    structural disclosures, and ML model predictions.
    """
    # 1. Detect Suspicious Indicators (Rule-based heuristics & structural checks)
    detected_indicators = detect_suspicious_indicators(
        text=text,
        job_title=job_title,
        company_name=company_name,
        requests_payment=requests_payment,
        requests_sensitive_info=requests_sensitive_info,
        interview_mode=interview_mode,
        company_url=company_url
    )
    
    # 2. Detect Positive Indicators
    positive_indicators = detect_positive_indicators(
        text=text,
        job_title=job_title,
        company_name=company_name,
        interview_mode=interview_mode,
        company_url=company_url
    )

    # 3. Compute Heuristic Base Score
    # Sum weights of detected indicators with diminishing returns for stacked flags
    raw_heuristic_weight = sum(ind['weight'] for ind in detected_indicators)
    # Scale non-linearly to 0-100 to prevent runaway scores while keeping high sensitivity
    # Formula: 100 * (1 - e^(-weight / 45))
    import math
    if raw_heuristic_weight > 0:
        heuristic_score = 100.0 * (1.0 - math.exp(-raw_heuristic_weight / 45.0))
    else:
        heuristic_score = 5.0  # Baseline baseline minimum screening floor

    # 4. Evaluate ML Model Prediction if model is trained and available
    model, vectorizer = load_ml_model(artifacts_dir)
    ml_score = None
    ml_confidence = None
    
    if model is not None and vectorizer is not None:
        try:
            processed_text = prepare_for_vectorizer(f"{job_title} {text}")
            X_vec = vectorizer.transform([processed_text])
            # Probability of fake/fraud class (class 1)
            probs = model.predict_proba(X_vec)[0]
            fake_prob = float(probs[1])
            ml_score = round(fake_prob * 100.0, 1)
            ml_confidence = round(float(max(probs)) * 100.0, 1)
        except Exception:
            ml_score = None
            ml_confidence = None

    # 5. Combined Score Fusion
    if ml_score is not None:
        # Weighted combination: 60% rule-based heuristics + 40% ML text model
        combined_score = (0.60 * heuristic_score) + (0.40 * ml_score)
    else:
        combined_score = heuristic_score

    # 6. Apply Positive Mitigations (up to -10 points reduction for verified safe signals)
    mitigation_points = min(12.0, len(positive_indicators) * 3.5)
    # Mitigations should not lower critical high-risk indicators below threshold
    has_critical_red_flag = any(ind['severity'] == 'high' for ind in detected_indicators)
    if has_critical_red_flag:
        # Cap mitigation to max 3 points if critical red flag exists
        mitigation_points = min(3.0, mitigation_points)
    
    final_score = max(0.0, combined_score - mitigation_points)

    # 7. Safety Floor: If blatant red flags like upfront fee or bank login demand are confirmed,
    # the score MUST not fall below high-risk threshold
    if any(ind['id'] in ['UPFRONT_FEE_DEMAND', 'BANKING_CREDENTIALS', 'EQUIPMENT_CHECK_SCAM'] for ind in detected_indicators):
        final_score = max(final_score, float(threshold_high))
    
    # Clamp score to 0.0 - 100.0
    final_score = round(min(100.0, max(0.0, final_score)), 1)

    # 8. Categorization based on configurable thresholds
    if final_score < threshold_low:
        risk_category = 'Lower Risk Indicators'
        risk_level = 'low'
    elif final_score < threshold_high:
        risk_category = 'Needs Further Verification'
        risk_level = 'medium'
    else:
        risk_category = 'Potentially Suspicious'
        risk_level = 'high'

    # 9. Recommendations
    recommended_actions = get_recommended_actions(final_score, detected_indicators)

    return {
        'risk_score': final_score,
        'risk_category': risk_category,
        'risk_level': risk_level,
        'ml_confidence': ml_confidence,
        'ml_score': ml_score,
        'heuristic_score': round(heuristic_score, 1),
        'detected_indicators': detected_indicators,
        'positive_indicators': positive_indicators,
        'recommended_actions': recommended_actions,
        'scoring_breakdown': {
            'heuristic_component': round(heuristic_score, 1),
            'ml_component': ml_score,
            'mitigation_points': round(mitigation_points, 1),
            'threshold_low': threshold_low,
            'threshold_high': threshold_high
        }
    }

