"""
Model Training Pipeline.
Trains a Scikit-learn TF-IDF + Logistic Regression classifier on labeled job posting data.
Includes train/test splitting, performance evaluation, and artifact serialization.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import joblib

# Add project root to sys.path
basedir = Path(__file__).resolve().parent.parent
if str(basedir) not in sys.path:
    sys.path.insert(0, str(basedir))

from ml.text_preprocessor import prepare_for_vectorizer
from ml.dataset import load_dataset


def train_and_evaluate(
    dataset_csv: str = None,
    output_dir: Path = None,
    random_seed: int = 42
) -> Dict[str, Any]:
    """
    Executes training and evaluation pipeline.
    """
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / 'artifacts'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print(" Fake Job Detection System - ML Training Pipeline ")
    print("==================================================")
    
    # 1. Load Dataset
    is_synthetic = dataset_csv is None or not Path(dataset_csv).exists()
    dataset_name = "Synthetic Reference Benchmark" if is_synthetic else f"Custom CSV ({dataset_csv})"
    print(f"[*] Dataset Source: {dataset_name}")
    if is_synthetic:
        print("[!] Note: Using explicitly identified synthetic dataset for demonstration and pipeline verification.")

    raw_texts, labels = load_dataset(dataset_csv)
    print(f"[*] Total samples loaded: {len(labels)} (Legitimate: {labels.count(0)}, Fraudulent: {labels.count(1)})")

    if len(labels) < 4:
        raise ValueError("Insufficient samples to train model.")

    # 2. Text Preprocessing
    print("[*] Normalizing and preprocessing text...")
    processed_texts = [prepare_for_vectorizer(t) for t in raw_texts]

    # 3. Stratified Train / Test Split
    test_size = 0.25 if len(labels) >= 8 else 0.5
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        processed_texts,
        labels,
        test_size=test_size,
        random_state=random_seed,
        stratify=labels if min(labels.count(0), labels.count(1)) >= 2 else None
    )
    print(f"[*] Train set size: {len(y_train)} | Test set size: {len(y_test)}")

    # 4. Feature Extraction (TF-IDF)
    print("[*] Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=2500,
        ngram_range=(1, 2),
        min_df=1,
        stop_words='english'
    )
    X_train_vec = vectorizer.fit_transform(X_train_raw)
    X_test_vec = vectorizer.transform(X_test_raw)

    # 5. Model Training (Logistic Regression)
    print("[*] Training Logistic Regression classifier...")
    classifier = LogisticRegression(
        C=1.0,
        class_weight='balanced',
        max_iter=500,
        random_state=random_seed
    )
    classifier.fit(X_train_vec, y_train)

    # 6. Evaluation on Unseen Test Data
    print("[*] Evaluating on held-out test split...")
    y_pred = classifier.predict(X_test_vec)
    y_pred_proba = classifier.predict_proba(X_test_vec)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    try:
        roc_auc = float(roc_auc_score(y_test, y_pred_proba))
    except Exception:
        roc_auc = None

    cm = confusion_matrix(y_test, y_pred).tolist()

    report = {
        "dataset_source": dataset_name,
        "is_synthetic": is_synthetic,
        "total_samples": len(labels),
        "train_samples": len(y_train),
        "test_samples": len(y_test),
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4) if roc_auc is not None else "N/A"
        },
        "confusion_matrix": cm,
        "random_seed": random_seed
    }

    print("\n--- Evaluation Results ---")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    if roc_auc is not None:
        print(f"ROC-AUC:   {roc_auc:.4f}")
    print(f"Confusion Matrix: {cm}")

    # 7. Persist Artifacts
    model_file = output_dir / 'job_classifier.joblib'
    vec_file = output_dir / 'tfidf_vectorizer.joblib'
    report_file = output_dir / 'training_report.json'

    joblib.dump(classifier, model_file)
    joblib.dump(vectorizer, vec_file)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n[+] Model saved to: {model_file}")
    print(f"[+] Vectorizer saved to: {vec_file}")
    print(f"[+] Metrics report saved to: {report_file}")
    print("==================================================\n")

    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train Job Fraud Detection Classifier")
    parser.add_argument('--dataset', type=str, default=None, help="Path to custom labeled CSV dataset")
    parser.add_argument('--output-dir', type=str, default=None, help="Output directory for artifacts")
    parser.add_argument('--seed', type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    out_path = Path(args.output_dir) if args.output_dir else None
    train_and_evaluate(dataset_csv=args.dataset, output_dir=out_path, random_seed=args.seed)

