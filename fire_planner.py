"""
FIRE Planner Agent
Computes corpus needed, monthly SIP, and generates
a month-by-month narrative roadmap using Claude.
"""

import json
import math
import anthropic

DISCLAIMER = "This is AI-generated analysis, not SEBI-registered investment advice."

FIRE_PROMPT = """You are an expert financial planner specialising in FIRE (Financial Independence, Retire Early) for Indian investors.

User profile:
{profile_json}

FIRE calculations:
- Years to FIRE: {years}
- Corpus needed (25x annual expenses): {corpus}
- Current savings future value: {fv_savings}
- Additional corpus needed: {gap}
- Required monthly SIP: {sip}
- Savings rate required: {savings_rate}%

Provide:
1. A realistic assessment of whether this FIRE plan is achievable
2. Recommended asset allocation (equity/debt/gold split) by decade
3. Top 3 specific mutual funds to invest in for this goal
4. Risk factors they must plan for (inflation, health, job loss)
5. A simple 3-phase roadmap: Foundation (0-5yr), Growth (5-15yr), Harvest (15yr+)

Be motivating but honest. Use Indian context. Give specific numbers.
"""

class FirePlannerAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def _future_value(self, pv: float, rate_annual: float, years: int) -> float:
        """Future value of a lump sum."""
        return pv * ((1 + rate_annual / 100) ** years)

    def _sip_required(self, target: float, rate_annual: float, years: int) -> float:
        """Monthly SIP needed to reach target."""
        r = rate_annual / 100 / 12
        n = years * 12
        if r == 0:
            return target / n
        return target * r / ((1 + r) ** n - 1)

    async def plan(self, data: dict) -> dict:
        age          = data["age"]
        income       = data["income"]
        expenses     = data["expenses"]
        savings      = data["savings"]
        target_age   = data["target_age"]
        ret          = data["expected_return"]

        years        = target_age - age
        annual_exp   = expenses * 12
        corpus       = annual_exp * 25          # 4% safe withdrawal rule
        fv_savings   = self._future_value(savings, ret, years)
        gap          = max(0, corpus - fv_savings)
        sip          = self._sip_required(gap, ret, years)
        savings_rate = round((sip / income) * 100, 1)

        # Milestone projections (every 5 years)
        milestones = []
        monthly_rate = ret / 100 / 12
        for yr in range(5, years + 1, 5):
            n = yr * 12
            fv_sav = self._future_value(savings, ret, yr)
            fv_sip = sip * ((1 + monthly_rate) ** n - 1) / monthly_rate if monthly_rate else sip * n
            total  = fv_sav + fv_sip
            milestones.append({
                "year": age + yr,
                "corpus_projected": round(total, 0),
                "target_pct": round((total / corpus) * 100, 1)
            })

        prompt = FIRE_PROMPT.format(
            profile_json=json.dumps(data, indent=2),
            years=years,
            corpus=int(corpus),
            fv_savings=int(fv_savings),
            gap=int(gap),
            sip=int(sip),
            savings_rate=savings_rate
        )
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "inputs": data,
            "fire_summary": {
                "years_to_fire": years,
                "corpus_needed": int(corpus),
                "current_savings_fv": int(fv_savings),
                "gap": int(gap),
                "monthly_sip_required": int(sip),
                "savings_rate_pct": savings_rate
            },
            "milestones": milestones,
            "ai_roadmap": response.content[0].text,
            "disclaimer": DISCLAIMER
        }
