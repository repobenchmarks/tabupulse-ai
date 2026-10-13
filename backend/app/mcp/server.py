import sys
import json
import asyncio
from typing import Dict, Any, List, Optional
from mcp.server.mcpserver import MCPServer
import pandas as pd

from backend.app.agents.data_agent import DataAgent
from backend.app.agents.revenue_agent import RevenueAgent
from backend.app.core.tabpfn_engine import TabPFNEngine

# Initialize MCP Server
mcp_server = MCPServer("tabupulse-agent")

data_agent = DataAgent()
revenue_agent = RevenueAgent()
tabpfn_engine = TabPFNEngine()

@mcp_server.tool()
def tabpfn_inspect_dataset(csv_content: str) -> str:
    """
    Analyzes raw tabular CSV data, infers column schemas, data types,
    and automatically identifies the target column for TabPFN training.
    """
    try:
        df = data_agent.load_csv(csv_content)
        result = data_agent.inspect_dataset(df)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp_server.tool()
def tabpfn_predict(csv_content: str, target_column: Optional[str] = None) -> str:
    """
    Trains TabPFN zero-shot on the provided tabular dataset and generates
    instant predictions, confidence intervals, accuracy scores, and feature importances.
    """
    try:
        df = data_agent.load_csv(csv_content)
        target = target_column
        if not target:
            inspection = data_agent.inspect_dataset(df)
            target = inspection["recommended_target"]

        prepared = data_agent.prepare_data_for_tabpfn(df, target)
        task_type = prepared["task_type"]

        if task_type == "classification":
            output = tabpfn_engine.fit_predict_classification(
                X_train=prepared["X_train"],
                y_train=prepared["y_train"],
                X_test=prepared["X_test"],
                y_test=prepared["y_test"],
                feature_names=prepared["feature_names"]
            )
        else:
            output = tabpfn_engine.fit_predict_regression(
                X_train=prepared["X_train"],
                y_train=prepared["y_train"],
                X_test=prepared["X_test"],
                y_test=prepared["y_test"],
                feature_names=prepared["feature_names"]
            )

        output["target_column"] = target
        output["test_rows_count"] = len(prepared["y_test"])
        return json.dumps(output, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp_server.tool()
def tabpfn_revenue_action_plan(csv_content: str, target_column: Optional[str] = None, domain: str = "ecommerce") -> str:
    """
    Generates an automated revenue action plan (retention playbook or invoice cashflow protection)
    with quantified dollar amounts at risk and tactical interventions.
    """
    try:
        df = data_agent.load_csv(csv_content)
        target = target_column or ("churned" if "churned" in df.columns else ("late_payment" if "late_payment" in df.columns else df.columns[-1]))

        prepared = data_agent.prepare_data_for_tabpfn(df, target)
        pred_res = tabpfn_engine.fit_predict_classification(
            X_train=prepared["X_train"],
            y_train=prepared["y_train"],
            X_test=prepared["X_test"],
            y_test=prepared["y_test"],
            feature_names=prepared["feature_names"]
        )

        test_records = prepared["test_original_df"]
        preds = pred_res["predictions"]
        probs = pred_res.get("probabilities")

        if domain.lower() == "ecommerce" or "churn" in target.lower():
            plan = revenue_agent.analyze_ecommerce_churn(test_records, preds, probs)
        else:
            plan = revenue_agent.analyze_freelance_cashflow(test_records, preds, probs, task_type="classification")

        plan["model_metrics"] = pred_res["metrics"]
        plan["engine"] = pred_res["engine"]
        return json.dumps(plan, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Run via stdio when launched from Claude Desktop or Cursor MCP config
    asyncio.run(mcp_server.run_stdio_async())
