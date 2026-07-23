import logging
from google import genai
from app.core.config import settings

logger = logging.getLogger("efficiency_v.ml.explainer")

SYSTEM_PROMPT = """You are a clinical decision support AI assistant for an Emergency Department triage system.
Your job is to explain a triage recommendation to the patient in clear, empathetic, and non-alarming language.

Rules:
- Always be calm, clear, and reassuring
- Use plain English — avoid complex medical jargon
- Explain WHY the triage level was recommended using the key health factors provided
- Keep the response to 2-3 short paragraphs
- Do NOT diagnose the patient — only explain the recommendation
- Do NOT use bullet points or lists — write in flowing paragraphs
- End with a brief statement of what will happen next at the hospital

Triage levels:
- Home Care: Safe to manage at home with self-care or follow-up with a regular doctor
- Consult: Needs medical evaluation but is not immediately life-threatening
- Immediate: Requires urgent or emergency attention — do not delay
"""

async def generate_explanation(
    original_complaint: str,
    prediction: str,
    confidence: float,
    top_features: list,
) -> str:
    """
    Calls Gemini to generate a patient-friendly explanation of the triage result.
    """
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # Build feature summary
        feature_lines = []
        for f in top_features:
            name = f["display_name"]
            val = f["value"]
            feature_lines.append(f"- {name}: {val}")
        features_text = "\n".join(feature_lines)

        user_message = f"""
Patient's chief complaint: "{original_complaint}"

Triage Recommendation: {prediction} (confidence: {confidence * 100:.1f}%)

Key health factors that influenced this recommendation:
{features_text}

Please write a clear, empathetic explanation for the patient explaining this triage recommendation and why it was given.
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_message,
            config={"system_instruction": SYSTEM_PROMPT}
        )

        return response.text

    except Exception as e:
        logger.error(f"Gemini explanation failed: {e}")
        return (
            f"Based on your reported symptoms, our system recommends: {prediction}. "
            "A healthcare professional will review your case and provide further guidance."
        )
