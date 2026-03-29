"""
Money Health Score Agent
Scores user across 6 financial dimensions and generates
a prioritised action plan using Claude.
"""

import json
import anthropic

DISCLAIMER = "This is AI-generated analysis, not SEBI-registered investment advice."

SCORE_PROMPT = """You are a personal financial wellness coach for Indian retail investors.

User's financial snapshot:
{data_json}

Dimension scores (out of 10):
{scores_json}

Overall score: {overall}/100

Provide:
1. The top 2 dimensions to fix immediately, with specific rupee targets
2. A 6-month action plan with monthly milestones
3. One "quick win" they can do this week that improves their score
4. Encouragement — many Indians are in a similar position, and small steps compound

Keep it warm, simple, and specific. No jargon. Use Indian context.
"""

class MoneyScoreAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def _score_emergency_fund(self, monthly_expenses: float, emergency_fund: float) -> dict:
        months_covered = emergency_fund / monthly_expenses if monthly_expenses else 0
        score = min(10, int(months_covered / 0.6))  # 6 months = 10/10
        return {"score": score, "label": "Emergency fund",
                "detail": f"{months_covered:.1f} months covered (target: 6 months)",
                "target": monthly_expenses * 6}

    def _score_insurance(self, monthly_income: float, term_cover: float) -> dict:
        annual_income = monthly_income * 12
        cover_multiple = term_cover / annual_income if annual_income else 0
        score = min(10, int(cover_multiple * 1.0))  # 10x income = 10/10
        return {"score": score, "label": "Insurance cover",
                "detail": f"{cover_multiple:.1f}x annual income covered (target: 10x)",
                "target": annual_income * 10}

    def _score_investments(self, monthly_income: float, equity: float, debt: float) -> dict:
        total = equity + debt
        annual_income = monthly_income * 12
        invest_ratio = total / annual_income if annual_income else 0
        equity_pct = (equity / total * 100) if total else 0
        # Score based on corpus size + diversification
        size_score = min(7, int(invest_ratio * 2))
        div_score  = 3 if 50 <= equity_pct <= 80 else 1
        score      = min(10, size_score + div_score)
        return {"score": score, "label": "Investment diversity",
                "detail": f"Equity {equity_pct:.0f}% / Debt {100 - equity_pct:.0f}% split"}

    def _score_debt(self, monthly_income: float, outstanding_loans: float) -> dict:
        annual_income = monthly_income * 12
        debt_ratio = outstanding_loans / annual_income if annual_income else 0
        # Lower debt = higher score
        score = max(0, 10 - int(debt_ratio * 2))
        return {"score": score, "label": "Debt health",
                "detail": f"Debt is {debt_ratio:.1f}x annual income (target: < 2x)"}

    def _score_tax(self, monthly_income: float, annual_tax_saved: float) -> dict:
        max_possible = 75000  # rough max via 80C + NPS + HRA
        ratio = annual_tax_saved / max_possible if max_possible else 0
        score = min(10, int(ratio * 10))
        return {"score": score, "label": "Tax efficiency",
                "detail": f"₹{int(annual_tax_saved):,} saved via deductions (target: ₹75,000+)"}

    def _score_retirement(self, age: int, monthly_income: float, retirement_corpus: float) -> dict:
        annual_income = monthly_income * 12
        years_to_60   = max(1, 60 - age)
        target_corpus = annual_income * 25  # 4% rule
        on_track_pct  = (retirement_corpus / target_corpus) * 100 if target_corpus else 0
        # Adjust for years remaining
        expected_pct  = ((60 - years_to_60) / 40) * 100  # linear expected progress
        score = min(10, int((on_track_pct / max(1, expected_pct)) * 10))
        return {"score": score, "label": "Retirement readiness",
                "detail": f"₹{int(retirement_corpus):,} saved of ₹{int(target_corpus):,} target"}

    async def score(self, data: dict) -> dict:
        dimensions = {
            "emergency":   self._score_emergency_fund(data["monthly_expenses"], data["emergency_fund"]),
            "insurance":   self._score_insurance(data["monthly_income"], data["term_cover"]),
            "investments": self._score_investments(data["monthly_income"], data["equity_investments"], data["debt_investments"]),
            "debt":        self._score_debt(data["monthly_income"], data["outstanding_loans"]),
            "tax":         self._score_tax(data["monthly_income"], data["annual_tax_saved"]),
            "retirement":  self._score_retirement(data["age"], data["monthly_income"], data["retirement_corpus"])
        }

        overall = round(sum(d["score"] for d in dimensions.values()) * 10 / 6, 0)

        scores_display = {k: {"score": v["score"], "detail": v["detail"]} for k, v in dimensions.items()}

        prompt = SCORE_PROMPT.format(
            data_json=json.dumps(data, indent=2),
            scores_json=json.dumps(scores_display, indent=2),
            overall=int(overall)
        )
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "overall_score": int(overall),
            "grade": "Excellent" if overall >= 80 else "Good" if overall >= 60 else "Needs attention" if overall >= 40 else "Critical",
            "dimensions": dimensions,
            "ai_action_plan": response.content[0].text,
            "disclaimer": DISCLAIMER
        }
