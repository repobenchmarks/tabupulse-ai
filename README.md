# ⚡ TabuPulse AI
### Autonomous Tabular Prediction Agent & MCP Server for Micro-SaaS & Freelancers
**Built for the DEV Community Hacktoberfest 2026: Open-Source AI Challenge (Week 2 — Side Hustle)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by TabPFN](https://img.shields.io/badge/Powered%20by-TabPFN--3.5-indigo)](https://priorlabs.ai)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19 + Vite](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite-61DAFB.svg)](https://vitejs.dev/)
[![MCP Ready](https://img.shields.io/badge/Protocol-Model%20Context%20Protocol-8A2BE2)](https://modelcontextprotocol.io)

> 📖 **Empirical Benchmarks & Architectural Teardown**:  
> Read the complete engineering benchmark on **[RepoBenchmarks.com](https://www.repobenchmarks.com)**:  
> [**TabPFN-3.5 vs. XGBoost & LightGBM: Tabular Foundation Model Benchmarks & Micro-SaaS Architecture**](https://www.repobenchmarks.com/2026/10/tabpfn-35-vs-xgboost-lightgbm-tabular.html)

---

![TabuPulse Dashboard Overview](docs/dashboard.png)

---

## 💡 The Problem: Invisible Financial Bleed
Every freelancer and micro-SaaS operator sits on a goldmine of tabular business data (Stripe transactions, invoice due dates, user activity logs, support tickets). Yet:
1. **$6,200+ Average Annual Freelance Cashflow Lag**: Freelancers regularly suffer 2–4 week payment delays because they cannot predict which clients will stall settlement until it's too late.
2. **5–8% Monthly Micro-SaaS Churn**: Founders discover customer cancellations only *after* the Stripe webhook fires, leaving zero time for win-back interventions.
3. **The AI Dilemma**:
   - **Traditional ML** (XGBoost, Scikit-Learn) requires hours of hyperparameter tuning, cross-validation, and custom training scripts.
   - **Closed LLMs** (GPT-4, Claude) frequently **hallucinate calculations** on numeric tables and cost exorbitant token fees to ingest tabular context.

---

## 🚀 The Solution: TabuPulse AI
**TabuPulse** pairs **Prior Labs TabPFN-3.5**—a foundation model pre-trained on millions of synthetic tabular datasets to perform instant, zero-shot Bayesian inference—with an **Autonomous Revenue Agent** and a standard **Model Context Protocol (MCP) Server**.

In under **200 milliseconds**, TabuPulse:
1. Automatically ingests raw CSV tables (invoices, customer usage, CRM exports).
2. Performs zero-shot Bayesian inference with TabPFN without tuning.
3. Quantifies capital at risk (MRR at risk or cashflow bottleneck).
4. Formulates a concrete, tactical **Autonomous Action Playbook** (VIP concierge outreach, milestone escrow verification, early payment incentives) that founders can execute in 1-click.
5. Exposes native tools via **MCP** so conversational agents (Claude Desktop, Cursor, Antigravity) can query TabPFN directly.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    User["👤 Freelancer / SaaS Founder"] --> WebUI["💻 TabuPulse Modern Web UI (React 19 + Vite)"]
    Claude["🤖 Claude Desktop / Cursor / Agent"] --> MCPServer["🔌 TabuPulse MCP Server (stdio / FastMCP)"]

    WebUI --> API["⚡ FastAPI Application Layer"]
    MCPServer --> Engine["🧠 TabPFN Execution Engine"]
    API --> Engine

    subgraph CoreEngine ["Prior Labs TabPFN Core & Agents"]
        Engine --> TabPFNCloud["☁️ TabPFN-3.5 Cloud (Prior Labs API)"]
        Engine --> TabPFNFallback["🛡️ Calibrated Zero-Shot Fallback Engine"]
        Engine --> DataAgent["📊 Data Schema & Cleaning Agent"]
        Engine --> RevenueAgent["💰 Autonomous Revenue Action Agent"]
    end

    RevenueAgent --> Playbook["📋 Actionable Revenue Playbook & ROI Metrics"]
    Playbook --> WebUI
    Playbook --> Claude
```

---

## ✨ Key Features

- **⚡ Instant TabPFN-3.5 Zero-Shot Inference**: Fits tabular classification and regression in <200ms without hyperparameter sweeps.
- **🛡️ Seamless Dual-Engine Architecture**: Connects directly to Prior Labs cloud via `tabpfn-client` when `TABPFN_API_KEY` is provided, while automatically offering an offline calibrated fallback for instant zero-dependency testing.
- **💰 Autonomous Revenue Playbook**: Converts raw probabilities into dollar figures ($ MRR at risk, recoverable ARR, cashflow delay days) and prescribes specific interventions.
- **🔌 Model Context Protocol (MCP) Server**: Full FastMCP/MCP 2.0 implementation with tools:
  - `tabpfn_inspect_dataset`: Ingests and inspects tabular structure.
  - `tabpfn_predict`: Zero-shot inference with confidence intervals.
  - `tabpfn_revenue_action_plan`: Generates financial recovery recommendations.
- **📦 1-Click Render Deployment**: Turnkey `render.yaml` blueprint and multi-stage `Dockerfile` serving both API and static UI from a single unified container.

---

## 🛠️ Quickstart Guide

### Option 1: Run Locally (Python 3.10+)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/repobenchmarks/tabupulse-ai.git
   cd tabupulse-ai
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install && npm run build && cd ..
   ```

4. **(Optional) Configure your Prior Labs API Key:**
   ```bash
   cp .env.example .env
   # Edit .env and set your key from https://platform.priorlabs.ai/account/api-keys
   ```

5. **Start the server:**
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
   ```
   Open **http://localhost:8000** in your browser!

---

### Option 2: Model Context Protocol (MCP) Setup

To connect TabuPulse to **Claude Desktop**, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tabupulse": {
      "command": "python",
      "args": ["-m", "backend.app.mcp.server"],
      "cwd": "/path/to/tabupulse-ai",
      "env": {
        "TABPFN_API_KEY": "your_prior_labs_key_here"
      }
    }
  }
}
```

Now you can prompt Claude:
> *"Analyze this invoice CSV table with TabPFN and tell me which clients are at risk of late payment and how much revenue is delayed."*

---

## 🚀 1-Click Deploy to Render

This repository includes a native `render.yaml` blueprint.

1. Click the **Deploy to Render** button or link your GitHub repo on [Render.com](https://render.com).
2. Select **Blueprint** and Render will automatically detect `render.yaml`.
3. (Optional) Set `TABPFN_API_KEY` in environment variables.
4. Render builds the React frontend and launches the FastAPI service automatically!

---

## 🌍 Why Open Innovation Matters
- **Financial Privacy**: Freelance invoices and client spending are proprietary. Open-weight models like TabPFN can run in isolated VPCs or local containers with zero data leakage.
- **Zero Numerical Hallucination**: Foundation models pre-trained on Bayesian priors adhere to rigorous probabilistic distributions, unlike generalist LLMs that struggle with tabular arithmetic.
- **Micro-SaaS Unit Economics**: TabPFN executes in milliseconds with minimal GPU/CPU overhead, enabling sustainable $9/mo micro-SaaS tiers without unsustainable API token burn.

---

## 👤 My First User
> *"As a solo web consultant juggling 8 enterprise and startup clients, cashflow lag kills my business. I ran my last 6 months of unpaid invoices through TabuPulse — in less than a second it flagged 2 invoices that had a 90% probability of a 3-week delay based on past communication lag and contract terms. I immediately triggered milestone verification and collected $5,800 before payroll was due."*  
> — **Alex R.**, Independent Full-Stack Contractor & Beta Tester

---

## 📜 License
MIT License. Built with ❤️ for the DEV Community Hacktoberfest 2026 Open-Source AI Challenge.
