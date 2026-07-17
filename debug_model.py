"""
debug_model.py  — run this to diagnose why the model always predicts 0.0000

  python debug_model.py
"""
import sys, os, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("=" * 60)
print("DEBUG: Model + Scaler Diagnostic")
print("=" * 60)

# ── 1. Check which model files exist ─────────────────────────────────────────
for fname in ["models/xgboost_fraud.ubj", "models/xgboost_fraud.pkl",
              "models/scaler.pkl", "models/ml_metrics.json"]:
    size = os.path.getsize(fname) if os.path.exists(fname) else -1
    ts   = os.path.getmtime(fname) if os.path.exists(fname) else 0
    import time
    print(f"  {'EXISTS' if size >= 0 else 'MISSING':7s}  {fname}"
          + (f"  ({size:,} bytes, {time.strftime('%Y-%m-%d %H:%M', time.localtime(ts))})" if size >= 0 else ""))

# ── 2. Load the model and scaler ──────────────────────────────────────────────
print()
from ml_model import load_model
from utils import load_scaler

model = load_model()
print(f"Model type    : {type(model)}")
print(f"Best iteration: {getattr(model, 'best_iteration', 'N/A')}")
print(f"n_estimators  : {getattr(model, 'n_estimators', 'N/A')}")

scaler = load_scaler("models/scaler.pkl")
print(f"Scaler type   : {type(scaler)}")
print(f"Scaler n_feat : {scaler.n_features_in_}")
print(f"Scaler names  : {getattr(scaler, 'feature_names_in_', 'NO NAMES')}")
print(f"Scaler mean   : {scaler.mean_}")
print(f"Scaler scale  : {scaler.scale_}")

# ── 3. Run predictions on known test vectors ──────────────────────────────────
print()
print("─" * 60)
print("Raw predict_proba on test vectors (no scaler applied yet)")
print("─" * 60)

feature_names = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]

test_vectors = {
    "All zeros (default UI)":
        [0.0] * 30,
    "Known fraud pattern (V14=-5, V17=-3, V4=+3)":
        [50000.0, 0, 0, 0, 3.0] + [0.0]*9 + [-5.0] + [0.0]*2 + [-3.0] + [0.0]*11 + [150.0],
    "Random normal":
        [50000.0] + list(np.random.randn(28)) + [200.0],
}

for label, vec in test_vectors.items():
    df = pd.DataFrame([vec], columns=feature_names)
    prob = float(model.predict_proba(df)[0][1])
    print(f"  {label}")
    print(f"    → fraud_prob = {prob:.6f}  ({'FRAUD' if prob > 0.5 else 'LEGIT'})")

# ── 4. Now apply scaler and retry ─────────────────────────────────────────────
print()
print("─" * 60)
print("After applying scaler to Time + Amount")
print("─" * 60)

for label, vec in test_vectors.items():
    vec2 = list(vec)
    if scaler.n_features_in_ == 2:
        scaled_df = pd.DataFrame([[vec2[0], vec2[29]]], columns=["Time", "Amount"])
        s = scaler.transform(scaled_df)[0]
        vec2[0], vec2[29] = float(s[0]), float(s[1])
    elif scaler.n_features_in_ == 1:
        s = scaler.transform([[vec2[0]]])[0][0]
        vec2[0] = float(s)

    df = pd.DataFrame([vec2], columns=feature_names)
    prob = float(model.predict_proba(df)[0][1])
    print(f"  {label}")
    print(f"    → Time_scaled={vec2[0]:.4f}  Amount_scaled={vec2[29]:.4f}")
    print(f"    → fraud_prob  = {prob:.6f}  ({'FRAUD' if prob > 0.5 else 'LEGIT'})")

# ── 5. ml_metrics threshold ───────────────────────────────────────────────────
print()
if os.path.exists("models/ml_metrics.json"):
    with open("models/ml_metrics.json") as f:
        m = json.load(f)
    print("ml_metrics.json:", json.dumps(m, indent=2))
else:
    print("ml_metrics.json: MISSING")
