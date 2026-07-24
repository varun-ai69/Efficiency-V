from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
from typing import List, Any

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.profile import UserProfile
from app.models.triage import TriageSession
from app.schemas.user import UserResponse
from app.schemas.triage import TriageStartRequest, TriageAnswerRequest, TriageChatResponse, TriageVectorResponse, TriageSessionHistory
from app.ai.embedding.engine import embedding_engine

router = APIRouter(prefix="/triage", tags=["Triage Chat"])

@router.get("/history", response_model=List[TriageSessionHistory])
async def get_triage_history(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetch all past triage sessions for the current user."""
    stmt = select(TriageSession).where(TriageSession.user_id == current_user.id).order_by(TriageSession.created_at.desc())
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    return sessions

# The full list of 62 features the ML model expects for prediction
ML_FEATURES = [
    "chief_complaint", "age", "gender", "race", "lang", "insurance_status", "bmi", 
    "previous_ed_visits", "previous_admissions", "asthma", "copd", 
    "diabetes", "hypertension", "heart_disease", "chf", "kidney_disease", 
    "epilepsy", "anemia", "influenza", "uti", "dizziness", "fatigue", 
    "allergy", "takes_antihypertensive", "takes_diabetes_medicine", 
    "takes_inhaler", "takes_blood_thinner", "heart_rate", "systolic_bp", 
    "diastolic_bp", "respiratory_rate", "spo2", "body_temperature", 
    "symptom_duration", "symptom_severity", "pain_score", "pain_type", 
    "symptom_onset", "progression", "intermittent", "relieved_by_rest", 
    "radiating_pain", "chest_tightness", "neck_stiffness", "light_sensitivity", 
    "persistent_cough", "bloody_cough", "body_aches", "abdominal_tenderness", 
    "diarrhea", "burning_urination", "urinary_frequency", "leg_swelling", 
    "palpitations", "vision_changes", "recent_injury", "unconscious", 
    "unable_to_speak", "severe_bleeding", "seizure_active", "cyanosis", 
    "severe_shortness_of_breath"
]

# Mapping dictionaries exactly as trained
CC_LIST = sorted([
    "fall_trauma", "abdominal_pain", "chest_pain", "shortness_of_breath", 
    "back_pain", "stroke_symptoms", "urinary_symptoms", "headache", 
    "dizziness", "fever", "cough", "rash", "vomiting", "leg_swelling", 
    "sore_throat", "syncope", "palpitations", "seizure", "diarrhea", 
    "allergic_reaction"
])
CC_MAP = {cc: idx for idx, cc in enumerate(CC_LIST)}

ONSET_MAP = {"not_specified": 0, "gradual": 1, "acute": 2, "sudden": 3}
PROGRESSION_MAP = {"not_specified": 0, "better": 1, "same": 2, "worse": 3}
PAIN_MAP = {"not_specified": 0, "sharp": 1, "burning": 2, "crushing": 3, "stabbing": 4, "pressure": 5}

@router.post("/start", response_model=TriageChatResponse)
async def start_triage(
    request: TriageStartRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Match the complaint using FAISS embedding
    template_id, confidence = embedding_engine.match_complaint(request.complaint)
    
    if not template_id:
        template_id = "general"
        confidence = 0.0

    session = TriageSession(
        user_id=current_user.id,
        matched_template_id=template_id,
        confidence=confidence,
        original_text=request.complaint,
        status="in_progress",
        collected_features={},
        current_question_index=0
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    # Get the template to figure out the first question
    template = embedding_engine.get_template(template_id)
    features_to_ask = template.get("required_features", []) if template else []
    
    if len(features_to_ask) > 0:
        next_feature = features_to_ask[0]
        questions = template.get("follow_up_questions", {})
        msg = questions.get(next_feature, f"Can you tell me more about: {next_feature}?")
    else:
        # No questions for this template
        session.status = "completed"
        await db.commit()
        msg = "Thank you. We have all the information needed."
        next_feature = None

    return TriageChatResponse(
        session_id=session.id,
        status=session.status,
        matched_template=template_id,
        confidence=confidence,
        next_question_feature=next_feature,
        message=msg
    )

@router.post("/{session_id}/answer", response_model=TriageChatResponse)
async def answer_triage(
    session_id: int,
    request: TriageAnswerRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(TriageSession).where(TriageSession.id == session_id, TriageSession.user_id == current_user.id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session.status == "completed":
        return TriageChatResponse(
            session_id=session.id,
            status=session.status,
            message="Session is already completed.",
            next_question_feature=None
        )

    # Save the answer
    # SQLAlchemy JSON mutations require re-assigning the dict
    collected = dict(session.collected_features)
    collected[request.feature_name] = request.feature_value
    session.collected_features = collected
    
    # Determine next question
    template = embedding_engine.get_template(session.matched_template_id)
    features_to_ask = template.get("required_features", []) if template else []
    
    session.current_question_index += 1
    
    if session.current_question_index < len(features_to_ask):
        next_feature = features_to_ask[session.current_question_index]
        questions = template.get("follow_up_questions", {})
        msg = questions.get(next_feature, f"Can you tell me more about: {next_feature}?")
    else:
        next_feature = None
        session.status = "completed"
        msg = "Thank you. Triage chat is complete."
        
    await db.commit()
    
    return TriageChatResponse(
        session_id=session.id,
        status=session.status,
        matched_template=session.matched_template_id,
        confidence=session.confidence,
        next_question_feature=next_feature,
        message=msg
    )

@router.get("/{session_id}/vector", response_model=TriageVectorResponse)
async def get_triage_vector(
    session_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(TriageSession).where(TriageSession.id == session_id, TriageSession.user_id == current_user.id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Triage chat is not completed yet.")
        
    # Fetch User Profile
    prof_stmt = select(UserProfile).where(UserProfile.user_id == current_user.id)
    prof_result = await db.execute(prof_stmt)
    profile = prof_result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=400, detail="User profile is missing. Cannot assemble full vector.")
        
    # Assemble the final vector
    vector: List[Any] = []
    
    for feature in ML_FEATURES:
        if feature == "chief_complaint":
            val = CC_MAP.get(session.matched_template_id, 0)
            vector.append(float(val))
            continue
            
        # 1. Check if it's in the static UserProfile
        if hasattr(profile, feature):
            vector.append(float(getattr(profile, feature)))
        # 2. Check if it was dynamically answered during the chat
        elif feature in session.collected_features:
            val = session.collected_features[feature]
            
            # Encode categorical strings if they match our maps
            if feature == "symptom_onset":
                val = ONSET_MAP.get(str(val).lower(), 0)
            elif feature == "progression":
                val = PROGRESSION_MAP.get(str(val).lower(), 0)
            elif feature == "pain_type":
                val = PAIN_MAP.get(str(val).lower(), 0)
            else:
                # Handle genuine user inputs for yes/no questions
                val_str = str(val).lower().strip()
                if val_str in ["yes", "y", "true", "1"]:
                    val = 1.0
                elif val_str in ["no", "n", "false", "0"]:
                    val = 0.0
                    
            try:
                vector.append(float(val))
            except ValueError:
                vector.append(0.0)
        # 3. Default missing
        else:
            vector.append(0.0)
                
    return TriageVectorResponse(
        session_id=session.id,
        user_id=current_user.id,
        vector=vector,
        feature_names=ML_FEATURES,
        message="Vector successfully assembled."
    )
