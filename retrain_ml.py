"""
retrain_ml.py
Standalone retraining script for the XGBoost ML fraud classifier (Module 1).

Fixes applied vs original:
  - Removed SMOTE: 344 real frauds -> 199k synthetic was extreme oversampling
    that hurt generalisation. XGBoost handles imbalance natively.
  - scale_pos_weight=577: native class weighting (284,315 legit / 492 fraud).
  - min_child_weight=1: allows splits with few samples (only 344 real frauds).
  - max_depth=6, n_estimators=1000, early_stopping_rounds=50: gives the model
    enough capacity and time to learn sparse fraud signal.
  - F-beta=2 threshold tuning on val set: favours recall over precision.

Usage:
    python retrain_ml.py

Outputs:
    models/xgboost_fraud.pkl   — retrained model
    models/scaler.pkl          — refitted scaler
    models/ml_metrics.json     — updated metrics (includes tuned threshold)
    plots/                     — confusion matrix + SHAP summary
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data_preprocessing import load_and_preprocess_ulb
from ml_model import train_xgboost, evaluate_model, explain_predictions, save_model
from utils import get_logger

logger = get_logger("retrain_ml")


def main():
    logger.info("=" * 60)
    logger.info("Retraining XGBoost ML Fraud Classifier")
    logger.info("No SMOTE | scale_pos_weight=577 | F-beta=2 threshold tuning")
    logger.info("=" * 60)

    X_train, X_val, X_test, y_train, y_val, y_test = load_and_preprocess_ulb()

    logger.info(f"Train size: {len(X_train):,} | fraud: {y_train.sum():,}")
    logger.info(f"Val size:  {len(X_val):,} | fraud: {y_val.sum():,}")
    logger.info(f"Test size: {len(X_test):,} | fraud: {y_test.sum():,}")

    model = train_xgboost(X_train, y_train, X_val, y_val)

    feature_names = X_test.columns.tolist()
    metrics = evaluate_model(model, X_test, y_test, X_val=X_val, y_val=y_val, feature_names=feature_names)
    explain_predictions(model, X_test, feature_names=feature_names)
    save_model(model)

    logger.info("=" * 60)
    logger.info("Retraining complete.")
    logger.info(f"  ROC-AUC : {metrics['roc_auc']}  (target > 0.95)")
    logger.info(f"  PR-AUC  : {metrics['pr_auc']}  (target > 0.75)")
    logger.info(f"  F1      : {metrics['f1']}  (target > 0.85)")
    logger.info("=" * 60)

    if metrics["roc_auc"] >= 0.95:
        logger.info("✓ ROC-AUC target met.")
    else:
        logger.warning(
            "ROC-AUC below 0.95. If using synthetic data, download the real "
            "creditcard.csv from Kaggle for production-quality results:\n"
            "  kaggle datasets download -d mlg-ulb/creditcardfraud -p data/raw/ --unzip"
        )


if __name__ == "__main__":
    main()
