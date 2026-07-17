import os
import sys
import json
import torch
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Ensure src modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.utils import get_logger, load_scaler
from src.ml_model import load_model
from src.fusion import predict_fraud
from src.cv_model import SiameseResNet, EMBEDDING_DIM

logger = get_logger(__name__)

# Global state to hold models
global_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load ML model only at startup (small, fast)
    try:
        logger.info("Loading XGBoost ML model...")
        global_models["ml"] = load_model("models/xgboost_fraud.ubj")
        if os.path.exists("models/scaler.pkl"):
            global_models["scaler"] = load_scaler("models/scaler.pkl")
        if os.path.exists("models/ml_metrics.json"):
            with open("models/ml_metrics.json") as f:
                metrics = json.load(f)
                global_models["metrics"] = metrics.get("threshold", 0.5)
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")

    logger.info("Server started successfully. NLP and CV models will load on first use.")
    yield
    global_models.clear()


def get_nlp_model():
    """Lazy-load NLP model on first request."""
    if "nlp" not in global_models:
        try:
            logger.info("Lazy-loading DistilBERT NLP model...")
            from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
            model_path = "models/distilbert_fraud"
            if os.path.isdir(model_path):
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                tokenizer = DistilBertTokenizer.from_pretrained(model_path)
                model = DistilBertForSequenceClassification.from_pretrained(model_path)
                model = model.to(device)
                model.eval()
                global_models["nlp"] = (model, tokenizer)
        except Exception as e:
            logger.error(f"Failed to load NLP model: {e}")
    return global_models.get("nlp")


def get_cv_model():
    """Lazy-load CV model on first request."""
    if "cv" not in global_models:
        try:
            logger.info("Lazy-loading SiameseResNet CV model...")
            cv_path = "models/siamese_resnet18.pt"
            if os.path.exists(cv_path):
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                # pretrained=False — weights come from the saved checkpoint, no internet download
                model = SiameseResNet(embedding_dim=EMBEDDING_DIM, pretrained=False)
                model.load_state_dict(torch.load(cv_path, map_location=device))
                model = model.to(device)
                model.eval()
                global_models["cv"] = model
        except Exception as e:
            logger.error(f"Failed to load CV model: {e}")
    return global_models.get("cv")

app = FastAPI(title="AI Fraud Guard", lifespan=lifespan)

# Setup Templates & Static Files
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "loaded_models": list(global_models.keys())}

@app.post("/api/predict")
async def predict(
    transaction_features: str = Form(None),
    transaction_text: str = Form(None),
    ref_image: UploadFile = File(None),
    test_image: UploadFile = File(None)
):
    """
    Unified prediction endpoint for ML, NLP, and CV.
    Handles multipart/form-data.
    """
    try:
        features = None
        if transaction_features:
            features = json.loads(transaction_features)
            
        text = None
        if transaction_text:
            text = transaction_text.strip()
            
        # Handle CV Images
        signature_paths = None
        if ref_image and test_image:
            import tempfile
            # Save uploaded files temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f_ref:
                f_ref.write(await ref_image.read())
                ref_path = f_ref.name
                
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f_test:
                f_test.write(await test_image.read())
                test_path = f_test.name
                
            signature_paths = (ref_path, test_path)

        result = predict_fraud(
            transaction_features=features,
            transaction_text=text,
            signature_paths=signature_paths,
            loaded_models={
                **global_models,
                # Inject lazy-loaded models only if actually needed
                **({}  if not text else {"nlp": get_nlp_model()} if get_nlp_model() else {}),
                **({}  if not signature_paths else {"cv": get_cv_model()} if get_cv_model() else {}),
            }
        )
        
        # Cleanup temporary image files
        if signature_paths:
            os.remove(signature_paths[0])
            os.remove(signature_paths[1])

        return JSONResponse(content=result)
    except Exception as e:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
