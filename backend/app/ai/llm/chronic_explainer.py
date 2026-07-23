import logging
import json
from google import genai
from pydantic import BaseModel
from typing import List

from app.core.config import settings

logger = logging.getLogger("efficiency_v.llm.chronic_explainer")

SYSTEM_PROMPT = """You are an empathetic, professional AI health coach specializing in Diabetes management.
You will be provided with a patient's health statistics over the last 7 days. These statistics have already been mathematically calculated and risk-stratified by our backend system.

Your job is to translate these numbers into a human-readable JSON response containing exactly three fields:
1. "patient_insight": A 2-3 sentence summary of how their week went. Be encouraging but honest. Focus on the relationship between their glucose, medication adherence, and exercise.
2. "actionable_nudges": A list of 2-3 short, highly actionable tips for next week based SPECIFICALLY on their data. (e.g. "Try walking for 10 minutes after dinner to help lower your post-meal spikes").
3. "clinician_summary": A dense, medical-grade summary of the week designed for a doctor to read in 5 seconds. Use medical terminology here.

Return ONLY a valid JSON object. Do not include markdown formatting like ```json."""

class ChronicLLMResponse(BaseModel):
    patient_insight: str
    actionable_nudges: List[str]
    clinician_summary: str

async def generate_weekly_insights(stats: dict) -> dict:
    """
    Calls Gemini to generate personalized weekly insights based on the pre-calculated math stats.
    """
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        user_message = f"""
Here is the patient's data for the past week:
- Days Logged: {stats['days_logged']} / 7
- Average Fasting Glucose: {stats.get('avg_fasting_glucose') or 'Not provided'} mg/dL
- Average Post-Meal Glucose: {stats.get('avg_post_meal_glucose') or 'Not provided'} mg/dL
- Medication Adherence: {stats.get('medication_adherence_pct')}%
- Total Exercise: {stats.get('total_exercise_minutes')} minutes
- Average Sleep: {stats.get('avg_sleep_hours') or 'Not provided'} hours
- Average Water Intake: {stats.get('avg_water_ml') or 'Not provided'} ml
- Average Weight: {stats.get('avg_weight_kg') or 'Not provided'} kg
- Average Blood Pressure: {stats.get('avg_systolic_bp') or 'Not provided'}/{stats.get('avg_diastolic_bp') or 'Not provided'} mmHg
- System Calculated Risk Level: {stats.get('risk_level')}

Generate the structured JSON response based on this data.
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_message,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "response_mime_type": "application/json",
                "response_schema": ChronicLLMResponse
            }
        )
        
        # Parse the JSON response returned by the model
        result = json.loads(response.text)
        return result

    except Exception as e:
        logger.error(f"Gemini chronic explainer failed: {e}")
        return {
            "patient_insight": "We couldn't generate your personalized insight right now, but your data is saved.",
            "actionable_nudges": ["Please keep logging your daily metrics!"],
            "clinician_summary": f"System Error during LLM generation. Raw stats: {stats}"
        }
