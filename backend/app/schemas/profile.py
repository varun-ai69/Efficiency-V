from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserProfileBase(BaseModel):
    age: int = Field(..., ge=0, le=120)
    gender: int = Field(0, description="0: Female, 1: Male, 2: Other")
    race: int = Field(0)
    lang: int = Field(0)
    insurance_status: int = Field(1)
    height_m: float = Field(..., gt=0.0, description="Height in meters")
    weight_kg: float = Field(..., gt=0.0, description="Weight in kilograms")
    previous_ed_visits: int = Field(0, ge=0)
    previous_admissions: int = Field(0, ge=0)

    # Medical Conditions
    asthma: float = 0.0
    copd: float = 0.0
    diabetes: float = 0.0
    hypertension: float = 0.0
    heart_disease: float = 0.0
    chf: float = 0.0
    kidney_disease: float = 0.0
    epilepsy: float = 0.0
    anemia: float = 0.0
    influenza: float = 0.0
    uti: float = 0.0
    dizziness: float = 0.0
    fatigue: float = 0.0
    allergy: float = 0.0

    # Medications
    takes_antihypertensive: float = 0.0
    takes_diabetes_medicine: float = 0.0
    takes_inhaler: float = 0.0
    takes_blood_thinner: float = 0.0


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[int] = None
    race: Optional[int] = None
    lang: Optional[int] = None
    insurance_status: Optional[int] = None
    height_m: Optional[float] = Field(None, gt=0.0)
    weight_kg: Optional[float] = Field(None, gt=0.0)
    previous_ed_visits: Optional[int] = Field(None, ge=0)
    previous_admissions: Optional[int] = Field(None, ge=0)
    
    asthma: Optional[float] = None
    copd: Optional[float] = None
    diabetes: Optional[float] = None
    hypertension: Optional[float] = None
    heart_disease: Optional[float] = None
    chf: Optional[float] = None
    kidney_disease: Optional[float] = None
    epilepsy: Optional[float] = None
    anemia: Optional[float] = None
    influenza: Optional[float] = None
    uti: Optional[float] = None
    dizziness: Optional[float] = None
    fatigue: Optional[float] = None
    allergy: Optional[float] = None
    
    takes_antihypertensive: Optional[float] = None
    takes_diabetes_medicine: Optional[float] = None
    takes_inhaler: Optional[float] = None
    takes_blood_thinner: Optional[float] = None


class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    bmi: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
