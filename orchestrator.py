"""
Orchestrator Agent — routes user queries to the right specialist agent
and handles general financial Q&A with SEBI compliance guardrails.
"""

import anthropic
import json

SYSTEM_PROMPT = """You are AI Money Mentor, an intelligent financial assistant built for Indian retail investors.
You have access to four specialist agents:
- MF X-Ray: Analyses mutual fund portfolios (CAMS/KFintech statements)
- Tax Wizard: Old vs new tax regime comparison, deduction finder
- FIRE Planner: Financial Independence Retire Early roadmap
- Money Score: 6-dimension financial health score

Rules you MUST follow:
1. Always end financial advice with: "This is AI-generated analysis, not SEBI-registered investment advice. Please consult a SEBI-registered advisor for personalised guidance."
2. Never guarantee returns. Use phrases like "historically", "based on past data".
3. Use Indian number formatting (lakhs, crores).
4. Be warm, simple, and jargon-free. Imagine explaining to a first-generation investor.
5. Always give specific rupee numbers, not vague advice.
"""

class OrchestratorAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()

    async def chat(self, message: str, context: dict) -> dict:
        context_str = json.dumps(context) if context else "No prior context."

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"User context: {context_str}\n\nUser question: {message}"
                }
            ]
        )

        return {
            "reply": response.content[0].text,
            "agent": "orchestrator",
            "disclaimer": "This is AI-generated analysis, not SEBI-registered investment advice."
        }
