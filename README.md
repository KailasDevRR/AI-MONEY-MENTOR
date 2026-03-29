🤖💰 AI Money Mentor

Making financial planning as accessible as checking WhatsApp.
An AI-powered personal finance mentor built for Indian retail investors.


📌 Problem Statement
95% of Indians have no financial plan.
Financial advisors charge ₹25,000+/year and serve only High Net-worth Individuals (HNIs).
AI Money Mentor democratises financial planning by embedding an intelligent AI mentor that turns confused savers into confident investors — for free.

✨ Features
1. 📊 MF Portfolio X-Ray
Upload your CAMS or KFintech statement and get in under 10 seconds:

Complete portfolio reconstruction
True XIRR per fund and overall
Overlap analysis between funds
Expense ratio drag calculation
Benchmark comparison
AI-generated rebalancing plan

2. 🏥 Money Health Score
A 5-minute onboarding flow that scores your financial wellness across 6 dimensions:
DimensionWhat it measuresEmergency FundMonths of expenses covered (target: 6 months)Insurance CoverTerm cover as multiple of income (target: 10×)Investment MixEquity/debt diversification qualityDebt HealthOutstanding loans vs annual income ratioTax EfficiencyDeductions utilised vs ₹75,000 maximumRetirement ReadinessCorpus on-track vs age-60 target
3. 🔥 FIRE Path Planner
Input your age, income, expenses, savings, and target retirement age to get:

Corpus needed (25× annual expenses — 4% rule)
Required monthly SIP amount
5-year milestone projections
3-phase roadmap: Foundation → Growth → Harvest
Recommended asset allocation by decade

4. 🧾 Tax Wizard
Input your salary structure and get:

Old vs New regime comparison (FY 2024-25 slabs)
HRA exemption calculation
Every deduction you're missing (80C, 80CCD, HRA)
Top tax-saving investments ranked by risk and liquidity
Exact rupee savings per regime


🏗️ Architecture
Browser (HTML/JS)
      │
      │  HTTP POST — JSON / FormData (PDF)
      ▼
┌─────────────────────────────────────────┐
│         FastAPI Gateway (Python)        │
│   CORS · Pydantic Validation · Routing  │
└─────────────────┬───────────────────────┘
                  │
      ┌───────────▼────────────┐
      │     AI Agent Layer     │
      │                        │
      │  MFXrayAgent           │
      │  FirePlannerAgent      │
      │  TaxWizardAgent        │
      │  MoneyScoreAgent       │
      │  OrchestratorAgent     │
      └───────────┬────────────┘
                  │
                  │  Anthropic Python SDK
                  ▼
      ┌───────────────────────┐
      │  Claude Sonnet-4 API  │
      │  claude-sonnet-4-     │
      │  20250514             │
      └───────────────────────┘

🛠️ Tech Stack
LayerTechnologyFrontendVanilla HTML5 / CSS3 / ES6 — zero dependenciesBackendFastAPI + Uvicorn (Python async)AI ModelAnthropic Claude (claude-sonnet-4-20250514)PDF ParsingpdfplumberFinancial Mathnumpy_financial + pure PythonValidationPydantic v2

🚀 Quick Start
Prerequisites

Python 3.9+
An Anthropic API key → https://console.anthropic.com

1. Clone the repo
bashgit clone https://github.com/YOUR_USERNAME/ai-money-mentor.git
cd ai-money-mentor
2. Set up the backend
bashcd backend
pip install -r requirements.txt
3. Add your API key
bashexport ANTHROPIC_API_KEY=your_key_here
4. Run the backend
bashuvicorn main:app --reload
# Runs at http://localhost:8000
5. Open the frontend
bashopen frontend/index.html
# Or serve with: python -m http.server 3000

📡 API Reference
MethodEndpointInputOutputGET/—Health checkPOST/api/mf-xrayCAMS/KFintech PDFPortfolio analysis + AI advicePOST/api/fire-plannerAge, income, goalsFIRE roadmap + milestonesPOST/api/tax-wizardSalary structureRegime comparison + deductionsPOST/api/money-scoreFinancial snapshot6-dimension score + action planPOST/api/chatFree-text questionGeneral financial Q&A

📁 Project Structure
ai-money-mentor/
├── frontend/
│   └── index.html          # Single-page UI (4 tabs)
├── backend/
│   ├── main.py             # FastAPI app + route definitions
│   ├── requirements.txt    # Python dependencies
│   └── agents/
│       ├── orchestrator.py # General Q&A + SEBI guardrails
│       ├── mf_xray.py      # Portfolio analysis agent
│       ├── fire_planner.py # FIRE calculation agent
│       ├── tax_wizard.py   # Tax regime comparison agent
│       └── money_score.py  # 6-dimension scoring agent
└── README.md


Additional guardrails:

Model is instructed to never guarantee returns
Uses phrases like "historically" and "based on past data"
Indian number formatting (lakhs/crores) throughout


🗺️ Roadmap

 Couple's Money Planner — joint income optimisation
 Life Event Advisor — bonus, inheritance, marriage, new baby
 WhatsApp integration
 SIP auto-execution via BSE StarMF API
 Multi-language support (Hindi, Tamil, Telugu)


🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first.

📄 License
MIT License — free to use, modify, and distribute.

Built for the ET Hackathon 2025
