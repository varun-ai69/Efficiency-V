from datetime import date, datetime, timezone
from sqlalchemy import Column, Integer, Float, Boolean, String, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database.session import Base

class DailyLog(Base):
    """Stores daily check-ins for chronic patients (Diabetes focused for MVP)"""
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Track the actual calendar day of the log
    log_date = Column(Date, nullable=False, default=date.today)
    
    # Diabetes specific industry-standard metrics
    fasting_glucose = Column(Float, nullable=True)      # Fasting Blood Sugar (mg/dL)
    post_meal_glucose = Column(Float, nullable=True)    # Postprandial Blood Sugar (mg/dL)
    
    medication_taken = Column(Boolean, nullable=False, default=False)
    exercise_minutes = Column(Integer, nullable=False, default=0)
    
    # New Fields based on user feedback
    sleep_hours = Column(Float, nullable=True)
    water_ml = Column(Integer, nullable=True)
    systolic_bp = Column(Integer, nullable=True)
    diastolic_bp = Column(Integer, nullable=True)
    diet_quality = Column(String, nullable=True) # Poor, Fair, Good, Excellent
    weight_kg = Column(Float, nullable=True)
    
    # E.g., "Ate some cake", "Felt dizzy"
    notes = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    user = relationship("User")


class WeeklyReport(Base):
    """Stores AI-generated weekly insights"""
    __tablename__ = "weekly_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # Mathematical aggregations
    avg_fasting_glucose = Column(Float, nullable=True)
    avg_post_meal_glucose = Column(Float, nullable=True)
    medication_adherence_pct = Column(Float, nullable=False)
    total_exercise_minutes = Column(Integer, nullable=False)
    
    # "Low", "Medium", "High"
    risk_level = Column(String, nullable=False)

    # LLM Generated JSON Outputs
    patient_insight = Column(String, nullable=False)
    actionable_nudges = Column(JSON, nullable=False)  # List of string nudges
    clinician_summary = Column(String, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    user = relationship("User")
