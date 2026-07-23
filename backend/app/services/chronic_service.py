from typing import List, Dict, Any
from app.models.chronic import DailyLog

def analyze_weekly_trends(logs: List[DailyLog]) -> Dict[str, Any]:
    """
    Evaluates 7 days of DailyLogs using deterministic math.
    Returns calculated averages, adherence rates, and a risk level.
    """
    if not logs:
        return {
            "avg_fasting_glucose": None,
            "avg_post_meal_glucose": None,
            "medication_adherence_pct": 0.0,
            "total_exercise_minutes": 0,
            "risk_level": "Unknown",
            "days_logged": 0
        }

    days_logged = len(logs)
    
    # Calculate Fasting Glucose Avg
    fasting_logs = [log.fasting_glucose for log in logs if log.fasting_glucose is not None]
    avg_fasting = sum(fasting_logs) / len(fasting_logs) if fasting_logs else None

    # Calculate Post-Meal Glucose Avg
    post_meal_logs = [log.post_meal_glucose for log in logs if log.post_meal_glucose is not None]
    avg_post_meal = sum(post_meal_logs) / len(post_meal_logs) if post_meal_logs else None

    # Calculate Medication Adherence
    meds_taken = sum(1 for log in logs if log.medication_taken)
    adherence_pct = round((meds_taken / days_logged) * 100, 2)

    # Calculate Total Exercise
    total_exercise = sum(log.exercise_minutes for log in logs if log.exercise_minutes)

    # Calculate New Averages
    sleep_logs = [log.sleep_hours for log in logs if log.sleep_hours is not None]
    avg_sleep = sum(sleep_logs) / len(sleep_logs) if sleep_logs else None

    water_logs = [log.water_ml for log in logs if log.water_ml is not None]
    avg_water = sum(water_logs) / len(water_logs) if water_logs else None
    
    weight_logs = [log.weight_kg for log in logs if log.weight_kg is not None]
    avg_weight = sum(weight_logs) / len(weight_logs) if weight_logs else None
    
    sys_logs = [log.systolic_bp for log in logs if log.systolic_bp is not None]
    avg_sys = sum(sys_logs) / len(sys_logs) if sys_logs else None
    
    dia_logs = [log.diastolic_bp for log in logs if log.diastolic_bp is not None]
    avg_dia = sum(dia_logs) / len(dia_logs) if dia_logs else None

    # Determine Risk Level mathematically
    risk_level = "Low"
    
    # High Risk triggers
    if avg_fasting and avg_fasting > 180:
        risk_level = "High"
    elif avg_post_meal and avg_post_meal > 250:
        risk_level = "High"
    elif adherence_pct < 50:
        risk_level = "High"
        
    # Medium Risk triggers (only if not already High)
    elif risk_level != "High":
        if avg_fasting and avg_fasting > 140:
            risk_level = "Medium"
        elif avg_post_meal and avg_post_meal > 180:
            risk_level = "Medium"
        elif adherence_pct < 80:
            risk_level = "Medium"

    return {
        "avg_fasting_glucose": round(avg_fasting, 1) if avg_fasting else None,
        "avg_post_meal_glucose": round(avg_post_meal, 1) if avg_post_meal else None,
        "medication_adherence_pct": adherence_pct,
        "total_exercise_minutes": total_exercise,
        "avg_sleep_hours": round(avg_sleep, 1) if avg_sleep else None,
        "avg_water_ml": round(avg_water, 0) if avg_water else None,
        "avg_weight_kg": round(avg_weight, 1) if avg_weight else None,
        "avg_systolic_bp": round(avg_sys, 0) if avg_sys else None,
        "avg_diastolic_bp": round(avg_dia, 0) if avg_dia else None,
        "risk_level": risk_level,
        "days_logged": days_logged
    }
