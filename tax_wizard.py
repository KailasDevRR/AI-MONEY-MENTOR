"""
Tax Wizard Agent
Compares old vs new Indian income tax regime,
surfaces missed deductions, and gives personalized advice via Claude.
"""

import json
import anthropic

DISCLAIMER = "This is AI-generated analysis, not SEBI-registered investment advice."

TAX_PROMPT = """You are an expert Indian tax advisor.

Given this salary and investment data:
{data_json}

Old regime taxable income: {old_taxable}
Old regime tax: {old_tax}
New regime taxable income: {new_taxable}
New regime tax: {new_tax}
Recommended regime: {rec_regime}
Tax saving: {tax_saving}

Provide:
1. Which regime they should choose and exactly why
2. List every deduction they are NOT fully utilizing with exact amounts
3. Top 3 tax-saving investments ranked by liquidity and risk
4. Specific steps to reduce their tax by the maximum possible amount

Be specific with rupee numbers. Keep it simple for a first-time taxpayer.
"""

class TaxWizardAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def _tax_old_regime(self, income: float) -> float:
        """Old regime slab tax (FY 2024-25)."""
        if income <= 250000:
            return 0
        elif income <= 500000:
            return (income - 250000) * 0.05
        elif income <= 1000000:
            return 12500 + (income - 500000) * 0.20
        elif income <= 5000000:
            return 112500 + (income - 1000000) * 0.30
        else:
            return 1612500 + (income - 5000000) * 0.30

    def _tax_new_regime(self, income: float) -> float:
        """New regime slab tax (FY 2024-25 revised)."""
        if income <= 300000:
            return 0
        elif income <= 700000:
            return (income - 300000) * 0.05
        elif income <= 1000000:
            return 20000 + (income - 700000) * 0.10
        elif income <= 1200000:
            return 50000 + (income - 1000000) * 0.15
        elif income <= 1500000:
            return 80000 + (income - 1200000) * 0.20
        else:
            return 140000 + (income - 1500000) * 0.30

    def _hra_exemption(self, basic: float, hra: float, rent_paid: float, city_type: str) -> float:
        """HRA exemption = min of 3 conditions."""
        hra_limit = basic * 0.50 if city_type == "metro" else basic * 0.40
        hra_actual = max(0, rent_paid - (basic * 0.10))
        return min(hra, hra_limit, hra_actual)

    async def analyse(self, data: dict) -> dict:
        basic        = data["basic"]
        hra_received = data["hra"]
        rent_paid    = data["rent_paid"]
        c80          = min(150000, data["investments_80c"])
        nps          = min(50000, data["nps_80ccd"])
        city         = data.get("city_type", "metro")

        gross = basic + hra_received

        # Old regime deductions
        hra_exempt   = self._hra_exemption(basic, hra_received, rent_paid, city)
        std_ded_old  = 50000
        old_taxable  = max(0, gross - hra_exempt - c80 - nps - std_ded_old)
        old_tax      = self._tax_old_regime(old_taxable) * 1.04  # +4% cess

        # New regime (standard deduction ₹75K from FY25)
        std_ded_new  = 75000
        new_taxable  = max(0, gross - std_ded_new)
        new_tax      = self._tax_new_regime(new_taxable) * 1.04

        rec_regime   = "Old regime" if old_tax < new_tax else "New regime"
        tax_saving   = abs(old_tax - new_tax)

        # Missed deductions
        missed = []
        if data["investments_80c"] < 150000:
            missed.append({"section": "80C", "shortfall": 150000 - data["investments_80c"],
                           "suggestion": "Top up ELSS/PPF/ULIP"})
        if data["nps_80ccd"] < 50000:
            missed.append({"section": "80CCD(1B) NPS", "shortfall": 50000 - data["nps_80ccd"],
                           "suggestion": "Invest in NPS Tier-1"})
        if rent_paid == 0:
            missed.append({"section": "HRA", "shortfall": 0,
                           "suggestion": "If you pay rent, declare it to claim HRA exemption"})

        # AI narrative
        prompt = TAX_PROMPT.format(
            data_json=json.dumps(data, indent=2),
            old_taxable=int(old_taxable),
            old_tax=int(old_tax),
            new_taxable=int(new_taxable),
            new_tax=int(new_tax),
            rec_regime=rec_regime,
            tax_saving=int(tax_saving)
        )
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "gross_income": gross,
            "old_regime": {"taxable_income": int(old_taxable), "tax": int(old_tax)},
            "new_regime": {"taxable_income": int(new_taxable), "tax": int(new_tax)},
            "recommended_regime": rec_regime,
            "you_save": int(tax_saving),
            "missed_deductions": missed,
            "ai_advice": response.content[0].text,
            "disclaimer": DISCLAIMER
        }
