from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Any

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.profile import UserProfile
from app.models.triage import TriageSession
from app.schemas.user import UserResponse
from app.ai.ml.predictor import triage_predictor
from app.ai.llm.explainer import generate_explanation
from app.api.v1.triage import ML_FEATURES, CC_MAP, ONSET_MAP, PROGRESSION_MAP, PAIN_MAP

router = APIRouter(prefix="/predict", tags=["ML Prediction"])


def _assemble_vector(profile: UserProfile, session: TriageSession) -> List[float]:
    """Assembles the full ML feature vector from profile + chat session answers."""
    vector: List[Any] = []
    for feature in ML_FEATURES:
        if feature == "chief_complaint":
            val = CC_MAP.get(session.matched_template_id, 0)
            vector.append(float(val))
            continue

        if hasattr(profile, feature):
            vector.append(float(getattr(profile, feature)))
        elif feature in session.collected_features:
            val = session.collected_features[feature]
            if feature == "symptom_onset":
                val = ONSET_MAP.get(str(val).lower(), 0)
            elif feature == "progression":
                val = PROGRESSION_MAP.get(str(val).lower(), 0)
            elif feature == "pain_type":
                val = PAIN_MAP.get(str(val).lower(), 0)
            else:
                val_str = str(val).lower().strip()
                if val_str in ["yes", "y", "true", "1"]:
                    val = 1.0
                elif val_str in ["no", "n", "false", "0"]:
                    val = 0.0
            try:
                vector.append(float(val))
            except (ValueError, TypeError):
                vector.append(0.0)
        else:
            vector.append(0.0)
    return vector


@router.post("/{session_id}")
async def predict_triage(
    session_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch session
    stmt = select(TriageSession).where(
        TriageSession.id == session_id,
        TriageSession.user_id == current_user.id
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Triage session not found")

    if session.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Triage chat must be completed before prediction. Keep answering questions."
        )

    # Fetch profile
    prof_stmt = select(UserProfile).where(UserProfile.user_id == current_user.id)
    prof_result = await db.execute(prof_stmt)
    profile = prof_result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=400,
            detail="User profile is missing. Please complete your profile first."
        )

    # Assemble vector
    vector = _assemble_vector(profile, session)

    # ML Prediction
    pred_result = triage_predictor.predict(vector, top_n=5)

    # LLM Explanation
    explanation = await generate_explanation(
        original_complaint=session.original_text or "unspecified complaint",
        prediction=pred_result["prediction"],
        confidence=pred_result["confidence"],
        top_features=pred_result["top_features"],
    )

    return {
        "session_id": session_id,
        "user_id": current_user.id,
        "original_complaint": session.original_text,
        "prediction": pred_result["prediction"],
        "label": pred_result["label"],
        "color": pred_result["color"],
        "confidence": pred_result["confidence"],
        "top_features": pred_result["top_features"],
        "explanation": explanation,
    }
