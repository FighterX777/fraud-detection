---
name: Financial Fraud Detection Context
description: Context and memory for the AI-Powered Financial Fraud Detection System, detailing architecture, modules (ML, NLP, CV), fusion layer, evaluation metrics, and anti-overfitting strategies.
---

# Financial Fraud Detection Project - Memory

This project is a multi-modal AI-Powered Financial Fraud Detection System. It combines machine learning on tabular transaction data, natural language processing on text (SMS/email), and computer vision on signature images to make a final unified fraud prediction.

## System Architecture

```
USER INPUT
    │
    ├──── Transaction Data (ML) ────────► XGBoost Classifier ──────────► ml_score (0.0-1.0) ──┐
    │                                                                                         │
    ├──── Text Input (NLP) ─────────────► DistilBERT (Fine-tuned) ─────► nlp_score (0.0-1.0) ─┼─► Weighted Fusion ──► Final Score & Verdict
    │                                                                                         │
    └──── Image Input (CV) ─────────────► Siamese ResNet18 ───────────► cv_score (0.0-1.0) ──┘
```

- **Fusion Formula**: `final_score = 0.5 * ml_score + 0.3 * nlp_score + 0.2 * cv_score` (re-weighted dynamically if some inputs are missing).
- **Decision Threshold**: `final_score > 0.5` is FRAUD, else LEGITIMATE.

---

## Codebase Modules

### 1. ML Module (XGBoost)
- **File**: `src/data_preprocessing.py`, `src/ml_model.py`
- **Dataset**: ULB Credit Card Fraud (284,807 txns, 492 fraud cases, 30 features: Time, V1-V28 PCA, Amount).
- **Preprocessing**: Scaled 'Amount' and 'Time' using `StandardScaler`. Stratified split (70% train, 15% val, 15% test). SMOTE on training set ONLY to handle class imbalance.
- **Model**: `XGBClassifier` with anti-overfitting parameters:
  - `max_depth=4`, `learning_rate=0.05`, `n_estimators=500`, `min_child_weight=5`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_alpha=0.1`, `reg_lambda=1.0`, `scale_pos_weight=577`, `eval_metric='aucpr'`, `early_stopping_rounds=20`.
- **Target Metrics**: ROC-AUC > 0.95, PR-AUC > 0.75, F1 > 0.85, Precision > 0.88, Recall > 0.82.
- **Explainability**: SHAP (TreeExplainer) to show feature importance and explain specific predictions.

### 2. NLP Module (DistilBERT)
- **File**: `src/nlp_model.py`
- **Dataset**: Combined SMS Spam Collection (UCI) + Phishing Email dataset.
- **Preprocessing**: Merge SMS and Email data, map label to binary (0 = legit, 1 = phishing/spam), tokenized via `DistilBertTokenizer` with `MAX_LEN=128`.
- **Model**: `DistilBertForSequenceClassification` fine-tuned on top 3 layers (freeze layers 0, 1, 2). Dropout = 0.1, Learning Rate = 2e-5, Epochs = 3 (max).
- **Target Metrics**: Accuracy > 0.92, F1 > 0.90, Precision > 0.91, Recall > 0.89.

### 3. CV Module (Siamese ResNet18)
- **File**: `src/cv_model.py`
- **Dataset**: CEDAR Signature Dataset (55 signers x 24 genuine + 24 forged = 2,640 images).
- **Preprocessing**: Create positive pairs (genuine, genuine -> 0) and negative pairs (genuine, forged -> 1). Image resized to 128x128. Training data augmentation (rotation, shear, jitter).
- **Model**: Siamese network with pretrained ResNet18 backbone. First two blocks frozen (`layer1`, `layer2`). Embeds images into 256-dim feature vectors. Distance measured via Euclidean distance. Trained using Contrastive Loss (`margin=1.0`).
- **Target Metrics**: Accuracy > 0.80, F1 > 0.78.

### 4. Fusion & Dashboard
- **File**: `src/fusion.py` - dynamically weights active module outputs and computes the final prediction.
- **File**: `app.py` - Streamlit dashboard with three tabs: "Transaction Analysis", "Text/SMS Check", and "Signature Verify".
- **File**: `train_all.py` - triggers training pipeline for ML, NLP, and CV models in sequence.

---

## Directory Structure
```
fraud_detection_project/
├── data/
│   ├── raw/                  # Downloaded datasets (creditcard.csv, sms_spam.csv, phishing_emails.csv, signatures/)
│   └── processed/            # Preprocessed datasets
├── src/
│   ├── data_preprocessing.py
│   ├── ml_model.py
│   ├── nlp_model.py
│   ├── cv_model.py
│   ├── fusion.py
│   └── utils.py
├── models/                   # Saved model binary weights (xgboost_fraud.pkl, distilbert_fraud/, siamese_resnet18.pt)
├── notebooks/                # EDA & training experimentation notebooks
├── app.py                    # Streamlit Dashboard
└── train_all.py              # Sequence runner for training models
```
