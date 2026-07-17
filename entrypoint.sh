#!/bin/sh
# ============================================================
# entrypoint.sh
# Container startup script for AI Fraud Detection System
# ============================================================
set -e

echo ""
echo "========================================================"
echo "  AI Fraud Guard — Container Startup"
echo "========================================================"

# ── 1. Inject Drive URLs into setup_assets.py if env vars set ─
# This allows the URLs to be passed via docker run -e or docker-compose
# without editing any files inside the image.

if [ -n "$MODELS_GDRIVE_URL" ] && [ "$MODELS_GDRIVE_URL" != "YOUR_MODELS_FILE_ID" ]; then
    echo "[entrypoint] Patching MODELS_GDRIVE_URL from environment..."
    python - <<PYEOF
import re, os

path = "setup_assets.py"
url  = os.environ["MODELS_GDRIVE_URL"]

with open(path) as f:
    content = f.read()

# Replace the placeholder line in the DOWNLOADS dict
content = re.sub(
    r'"gdrive":\s*"[^"]*"(?=.*"models")',   # won't work for multi-line, use block below
    f'"gdrive": "{url}"',
    content,
    count=1,
)

# More robust: replace the models gdrive value specifically
import ast, textwrap

# Simple string replacement for the models block
old_pattern = r'("models".*?"gdrive":\s*")[^"]*(")'
new_val     = rf'\g<1>{url}\g<2>'
content2    = re.sub(old_pattern, new_val, content, flags=re.DOTALL, count=1)
with open(path, "w") as f:
    f.write(content2)
print(f"  Patched models gdrive URL -> {url[:60]}...")
PYEOF
fi

if [ -n "$DATA_GDRIVE_URL" ] && [ "$DATA_GDRIVE_URL" != "" ]; then
    echo "[entrypoint] Patching DATA_GDRIVE_URL from environment..."
    python - <<PYEOF
import re, os

path = "setup_assets.py"
url  = os.environ["DATA_GDRIVE_URL"]

with open(path) as f:
    content = f.read()

old_pattern = r'("data".*?"gdrive":\s*")[^"]*(")'
new_val     = rf'\g<1>{url}\g<2>'
content2    = re.sub(old_pattern, new_val, content, flags=re.DOTALL, count=1)
with open(path, "w") as f:
    f.write(content2)
print(f"  Patched data gdrive URL -> {url[:60]}...")
PYEOF
fi

# ── 2. Download assets if models folder is missing/empty ──────
MODELS_DIR="models"
MODELS_UBJ="models/xgboost_fraud.ubj"
MODELS_PKL="models/xgboost_fraud.pkl"

if [ -f "$MODELS_UBJ" ] || [ -f "$MODELS_PKL" ]; then
    echo "[entrypoint] Models already present — skipping download."
else
    echo "[entrypoint] Models not found — running setup_assets.py..."
    echo "[entrypoint] Args: $SETUP_ASSETS_ARGS"
    python setup_assets.py $SETUP_ASSETS_ARGS
fi

# ── 3. Verify at least the ML model loaded ────────────────────
if [ ! -f "$MODELS_UBJ" ] && [ ! -f "$MODELS_PKL" ]; then
    echo ""
    echo "  WARNING: XGBoost model file not found after setup."
    echo "  The dashboard will launch but ML predictions will be disabled."
    echo "  Check that MODELS_GDRIVE_URL is set correctly."
    echo ""
fi

# ── 4. Launch FastAPI Server ────────────────────────────────────
echo ""
echo "[entrypoint] Starting FastAPI on port 8000..."
echo "========================================================"
echo ""

exec uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
