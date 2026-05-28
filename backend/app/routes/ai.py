"""AI insight routes — OpenAI runs only in backend services."""
from fastapi import APIRouter

from app.services.ai_openai_service import (
    generate_daily_summary,
    generate_insights_bundle,
    generate_weekly_report,
    is_ai_configured,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status")
async def ai_status():
    return {"configured": is_ai_configured(), "enabled": False}


@router.get("/insights")
async def get_insights():
    """Placeholder bundle for mobile AI Insights (future: auth + user context)."""
    return await generate_insights_bundle("anonymous")


@router.post("/daily-summary")
async def daily_summary(payload: dict):
    return await generate_daily_summary(payload)


@router.post("/weekly-report")
async def weekly_report(payload: dict):
    return await generate_weekly_report(payload)
