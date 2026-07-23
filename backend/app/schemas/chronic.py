from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class DailyLogCreate(BaseModel):
    log_date: Optional[date] = None # Defaults to today if not provided
    fasting_glucose: Optional[float] = Field(None, ge=20, le=600, description="Fasting Blood Sugar (mg/dL)")
    post_meal_glucose: Optional[float] = Field(None, ge=20, le=600, description="Postprandial Blood Sugar (mg/dL)")
    medication_taken: bool = False
    exercise_minutes: int = Field(0, ge=0, le=1440)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24, description="Hours of sleep")
    water_ml: Optional[int] = Field(None, ge=0, le=10000, description="Water intake in ml")
    systolic_bp: Optional[int] = Field(None, ge=50, le=250, description="Systolic Blood Pressure")
    diastolic_bp: Optional[int] = Field(None, ge=30, le=150, description="Diastolic Blood Pressure")
    diet_quality: Optional[str] = Field(None, description="Poor, Fair, Good, or Excellent")
    weight_kg: Optional[float] = Field(None, ge=20, le=300, description="Weight in kg")
    notes: Optional[str] = None

class DailyLogResponse(DailyLogCreate):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WeeklyReportResponse(BaseModel):
    id: int
    user_id: int
    start_date: date
    end_date: date
    avg_fasting_glucose: Optional[float]
    avg_post_meal_glucose: Optional[float]
    medication_adherence_pct: float
    total_exercise_minutes: int
    risk_level: str
    patient_insight: str
    actionable_nudges: List[str]
    clinician_summary: str
    created_at: datetime

    class Config:
        from_attributes = True
