"""
OpenAI integration layer — all LLM calls stay server-side.

Enable by setting OPENAI_API_KEY in backend/.env and flipping AI_ENABLED.
"""
from __future__ import annotations

import os
from typing import Any

from loguru import logger

AI_ENABLED = os.getenv("AI_FEATURES_ENABLED", "false").lower() == "true"


def is_ai_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY", "").strip())


async def generate_daily_summary(_nutrition_payload: dict[str, Any]) -> dict[str, Any]:
    """Future: send structured daily analytics to OpenAI and return summary text."""
    if not AI_ENABLED or not is_ai_configured():
        return {
            "summary": "AI summaries are not enabled yet. Log meals to unlock insights.",
            "source": "placeholder",
        }
    logger.info("OpenAI daily summary requested (not implemented)")
    return {"summary": "AI pipeline pending implementation.", "source": "stub"}


async def generate_weekly_report(_nutrition_payload: dict[str, Any]) -> dict[str, Any]:
    if not AI_ENABLED or not is_ai_configured():
        return {"report": "Weekly AI report will appear here once enabled.", "source": "placeholder"}
    return {"report": "AI pipeline pending implementation.", "source": "stub"}


async def generate_insights_bundle(_user_id: str) -> dict[str, Any]:
    """Aggregate endpoint for mobile AI Insights tab."""
    return {
        "dailySummary": await generate_daily_summary({}),
        "weeklyReport": await generate_weekly_report({}),
        "smartRecommendation": {
            "message": "Enable AI_FEATURES_ENABLED after OpenAI key is set.",
            "suggestedFoods": [],
        },
        "notificationSummary": {"message": "Notification insights will sync with meal data."},
        "healthPatterns": {"summary": "", "patterns": []},
        "source": "placeholder",
        "generatedAt": None,
    }
