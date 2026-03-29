"""
AI Money Mentor — FastAPI Backend
Agents: MF X-Ray, Tax Wizard, FIRE Planner, Money Health Score
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from agents.orchestrator import OrchestratorAgent
from agents.mf_xray import MFXrayAgent
from agents.tax_wizard import TaxWizardAgent
from agents.fire_planner import FirePlannerAgent
from agents.money_score import MoneyScoreAgent

app = FastAPI(title="AI Money Mentor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = OrchestratorAgent()
mf_agent     = MFXrayAgent()
tax_agent    = TaxWizardAgent()
fire_agent   = FirePlannerAgent()
score_agent  = MoneyScoreAgent()


# ── Request Models ─────────────────────────────────────────────────────────────

class FireInput(BaseModel):
    age: int
    income: float
    expenses: float
    savings: float
    target_age: int
    expected_return: float = 12.0

class TaxInput(BaseModel):
    basic: float
    hra: float
    rent_paid: float
    investments_80c: float
    nps_80ccd: float = 0
    city_type: str = "metro"

class MoneyScoreInput(BaseModel):
    monthly_income: float
    monthly_expenses: float
    emergency_fund: float
    term_cover: float
    equity_investments: float
    debt_investments: float
    outstanding_loans: float
    annual_tax_saved: float
    retirement_corpus: float
    age: int

class ChatInput(BaseModel):
    message: str
    context: Optional[dict] = None


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "AI Money Mentor is running", "version": "1.0.0"}


@app.post("/api/mf-xray")
async def mf_xray(file: UploadFile = File(...)):
    """Upload CAMS/KFintech PDF statement -> XIRR, overlap, rebalancing advice."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files accepted")
    contents = await file.read()
    result = await mf_agent.analyse(contents)
    return result


@app.post("/api/fire-planner")
async def fire_planner(data: FireInput):
    """Return FIRE roadmap with SIP breakdown and AI narrative."""
    result = await fire_agent.plan(data.dict())
    return result


@app.post("/api/tax-wizard")
async def tax_wizard(data: TaxInput):
    """Compare old vs new regime, surface missed deductions."""
    result = await tax_agent.analyse(data.dict())
    return result


@app.post("/api/money-score")
async def money_score(data: MoneyScoreInput):
    """Return 6-dimension money health score with action plan."""
    result = await score_agent.score(data.dict())
    return result


@app.post("/api/chat")
async def chat(data: ChatInput):
    """General financial Q&A routed through orchestrator agent."""
    result = await orchestrator.chat(data.message, data.context or {})
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
