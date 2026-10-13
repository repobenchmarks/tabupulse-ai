import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

from backend.app.core.config import settings
from backend.app.core.tabpfn_engine import TabPFNEngine
from backend.app.agents.data_agent import DataAgent
from backend.app.agents.revenue_agent import RevenueAgent

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Tabular Prediction Agent & MCP Server powered by TabPFN-3.5"
)

# Enable CORS for local dev and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_agent = DataAgent()
revenue_agent = RevenueAgent()
tabpfn_engine = TabPFNEngine()

DATA_DIR = Path(__file__).parent / "data"

SAMPLE_DATASETS = {
    "ecommerce_churn": {
        "id": "ecommerce_churn",
        "title": "E-Commerce / SaaS Customer Retention",
        "description": "Customer activity, support tickets, spend, and login intervals to forecast churn risk and protect monthly recurring revenue.",
        "filename": "sample_ecommerce_churn.csv",
        "default_target": "churned",
        "domain": "ecommerce"
    },
    "freelance_cashflow": {
        "id": "freelance_cashflow",
        "title": "Freelancer Invoice & Cashflow Risk",
        "description": "Invoice amounts, client tiers, and communication lag to predict late payment probability and safeguard freelancer runway.",
        "filename": "sample_freelance_cashflow.csv",
        "default_target": "late_payment",
        "domain": "freelance"
    }
}

class PredictRequest(BaseModel):
    dataset_id: Optional[str] = None
    csv_content: Optional[str] = None
    target_column: Optional[str] = None
    custom_record: Optional[Dict[str, Any]] = None

@app.get("/api/health")
def get_health():
    engine_status = tabpfn_engine.check_connection()
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "engine_info": engine_status,
        "features": {
            "tabpfn_cloud": engine_status["connected"],
            "fallback_engine": True,
            "mcp_server": True,
            "revenue_agent": True
        }
    }

@app.get("/api/sample-datasets")
def get_sample_datasets():
    datasets = []
    for key, val in SAMPLE_DATASETS.items():
        filepath = DATA_DIR / val["filename"]
        row_count = 0
        if filepath.exists():
            df = pd.read_csv(filepath)
            row_count = len(df)
        datasets.append({
            "id": val["id"],
            "title": val["title"],
            "description": val["description"],
            "default_target": val["default_target"],
            "domain": val["domain"],
            "total_records": row_count
        })
    return {"datasets": datasets}

@app.get("/api/sample-datasets/{dataset_id}")
def get_sample_dataset_detail(dataset_id: str):
    if dataset_id not in SAMPLE_DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")

    meta = SAMPLE_DATASETS[dataset_id]
    filepath = DATA_DIR / meta["filename"]
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Dataset file missing")

    df = pd.read_csv(filepath)
    inspection = data_agent.inspect_dataset(df)
    csv_text = df.to_csv(index=False)

    return {
        "metadata": meta,
        "inspection": inspection,
        "csv_content": csv_text
    }

@app.post("/api/analyze")
async def analyze_dataset(
    file: Optional[UploadFile] = File(None),
    dataset_id: Optional[str] = Form(None),
    csv_text: Optional[str] = Form(None)
):
    df = None
    if file:
        content = await file.read()
        df = data_agent.load_csv(content)
    elif dataset_id and dataset_id in SAMPLE_DATASETS:
        filepath = DATA_DIR / SAMPLE_DATASETS[dataset_id]["filename"]
        df = pd.read_csv(filepath)
    elif csv_text:
        df = data_agent.load_csv(csv_text)
    else:
        raise HTTPException(status_code=400, detail="Provide a file, dataset_id, or csv_text")

    inspection = data_agent.inspect_dataset(df)
    return {
        "status": "success",
        "inspection": inspection,
        "csv_content": df.to_csv(index=False)
    }

@app.post("/api/predict")
def run_prediction(req: PredictRequest):
    df = None
    domain = "ecommerce"

    if req.dataset_id and req.dataset_id in SAMPLE_DATASETS:
        meta = SAMPLE_DATASETS[req.dataset_id]
        filepath = DATA_DIR / meta["filename"]
        df = pd.read_csv(filepath)
        domain = meta["domain"]
    elif req.csv_content:
        df = data_agent.load_csv(req.csv_content)
        if "invoice" in req.csv_content.lower() or "freelance" in req.csv_content.lower():
            domain = "freelance"
    else:
        raise HTTPException(status_code=400, detail="Must provide dataset_id or csv_content")

    target = req.target_column
    if not target or target not in df.columns:
        inspection = data_agent.inspect_dataset(df)
        target = inspection["recommended_target"]

    prepared = data_agent.prepare_data_for_tabpfn(df, target)
    task_type = prepared["task_type"]

    if task_type == "classification":
        model_result = tabpfn_engine.fit_predict_classification(
            X_train=prepared["X_train"],
            y_train=prepared["y_train"],
            X_test=prepared["X_test"],
            y_test=prepared["y_test"],
            feature_names=prepared["feature_names"]
        )
    else:
        model_result = tabpfn_engine.fit_predict_regression(
            X_train=prepared["X_train"],
            y_train=prepared["y_train"],
            X_test=prepared["X_test"],
            y_test=prepared["y_test"],
            feature_names=prepared["feature_names"]
        )

    # Generate Revenue Action Playbook
    test_records = prepared["test_original_df"]
    preds = model_result["predictions"]
    probs = model_result.get("probabilities")

    if domain == "ecommerce" or "churn" in target.lower():
        revenue_playbook = revenue_agent.analyze_ecommerce_churn(test_records, preds, probs)
    else:
        revenue_playbook = revenue_agent.analyze_freelance_cashflow(test_records, preds, probs, task_type=task_type)

    return {
        "status": "success",
        "target_column": target,
        "task_type": task_type,
        "train_rows": prepared["train_size"],
        "test_rows": prepared["test_size"],
        "features_used": prepared["feature_names"],
        "model_result": model_result,
        "revenue_playbook": revenue_playbook
    }

@app.get("/api/mcp-info")
def get_mcp_info():
    return {
        "name": "tabupulse-agent",
        "description": "Model Context Protocol interface for TabPFN Tabular AI",
        "tools": [
            {
                "name": "tabpfn_inspect_dataset",
                "description": "Inspects tabular CSV, detects schema, column types, and targets."
            },
            {
                "name": "tabpfn_predict",
                "description": "Trains TabPFN zero-shot on tabular data, returning calibrated probabilities and metrics."
            },
            {
                "name": "tabpfn_revenue_action_plan",
                "description": "Generates automated tactical business interventions with ROI dollar amounts."
            }
        ],
        "claude_desktop_config_example": {
            "mcpServers": {
                "tabupulse": {
                    "command": "python",
                    "args": ["-m", "backend.app.mcp.server"],
                    "env": {
                        "TABPFN_API_KEY": "your_api_key_here"
                    }
                }
            }
        }
    }

# Serve frontend build in production / single-service deployment
from fastapi.staticfiles import StaticFiles
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

