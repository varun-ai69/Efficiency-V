from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, timedelta
from typing import List

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.schemas.user import UserResponse
from app.models.chronic import DailyLog, WeeklyReport
from app.schemas.chronic import DailyLogCreate, DailyLogResponse, WeeklyReportResponse
from app.services.chronic_service import analyze_weekly_trends
from app.ai.llm.chronic_explainer import generate_weekly_insights

router = APIRouter(prefix="/chronic", tags=["Chronic Disease (Phase 2)"])

@router.post("/log", response_model=DailyLogResponse)
async def create_daily_log(
    log_in: DailyLogCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a daily metric log for diabetes tracking"""
    log_date = log_in.log_date or date.today()
    
    # Check if log already exists for this date
    stmt = select(DailyLog).where(
        DailyLog.user_id == current_user.id,
        DailyLog.log_date == log_date
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A log already exists for {log_date}."
        )

    new_log = DailyLog(
        user_id=current_user.id,
        log_date=log_date,
        fasting_glucose=log_in.fasting_glucose,
        post_meal_glucose=log_in.post_meal_glucose,
        medication_taken=log_in.medication_taken,
        exercise_minutes=log_in.exercise_minutes,
        sleep_hours=log_in.sleep_hours,
        water_ml=log_in.water_ml,
        systolic_bp=log_in.systolic_bp,
        diastolic_bp=log_in.diastolic_bp,
        diet_quality=log_in.diet_quality,
        weight_kg=log_in.weight_kg,
        notes=log_in.notes
    )
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    return new_log

@router.get("/logs", response_model=List[DailyLogResponse])
async def get_recent_logs(
    days: int = 7,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetch the past X days of logs for charting"""
    start_date = date.today() - timedelta(days=days)
    stmt = select(DailyLog).where(
        DailyLog.user_id == current_user.id,
        DailyLog.log_date >= start_date
    ).order_by(DailyLog.log_date.desc())
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/report/generate", response_model=WeeklyReportResponse)
async def generate_weekly_report(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Core Engine for Phase 2:
    1. Fetches past 7 days of logs
    2. Calculates mathematical trend and risk
    3. Calls LLM for patient insight, nudges, and clinician summary
    4. Saves and returns the WeeklyReport
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=6) # Last 7 days inclusive

    # 1. Fetch Logs
    stmt = select(DailyLog).where(
        DailyLog.user_id == current_user.id,
        DailyLog.log_date >= start_date,
        DailyLog.log_date <= end_date
    ).order_by(DailyLog.log_date.asc())
    
    result = await db.execute(stmt)
    logs = result.scalars().all()

    if not logs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough data to generate a report. Please log at least one day."
        )

    # 2. Math/Trend Engine
    stats = analyze_weekly_trends(logs)

    # 3. AI/LLM Engine
    llm_response = await generate_weekly_insights(stats)

    # 4. Save the generated report
    report = WeeklyReport(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        avg_fasting_glucose=stats["avg_fasting_glucose"],
        avg_post_meal_glucose=stats["avg_post_meal_glucose"],
        medication_adherence_pct=stats["medication_adherence_pct"],
        total_exercise_minutes=stats["total_exercise_minutes"],
        risk_level=stats["risk_level"],
        patient_insight=llm_response["patient_insight"],
        actionable_nudges=llm_response["actionable_nudges"],
        clinician_summary=llm_response["clinician_summary"]
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)

    return report
