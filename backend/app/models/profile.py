from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Demographics
    age = Column(Integer, nullable=False)
    gender = Column(Integer, nullable=False)
    race = Column(Integer, nullable=False, default=0)
    lang = Column(Integer, nullable=False, default=0)
    insurance_status = Column(Integer, nullable=False, default=1)
    height_m = Column(Float, nullable=False, default=1.70)
    weight_kg = Column(Float, nullable=False, default=70.0)
    bmi = Column(Float, nullable=False)
    previous_ed_visits = Column(Integer, nullable=False, default=0)

    previous_admissions = Column(Integer, nullable=False, default=0)

    # Medical Conditions
    asthma = Column(Float, nullable=False, default=0.0)
    copd = Column(Float, nullable=False, default=0.0)
    diabetes = Column(Float, nullable=False, default=0.0)
    hypertension = Column(Float, nullable=False, default=0.0)
    heart_disease = Column(Float, nullable=False, default=0.0)
    chf = Column(Float, nullable=False, default=0.0)
    kidney_disease = Column(Float, nullable=False, default=0.0)
    epilepsy = Column(Float, nullable=False, default=0.0)
    anemia = Column(Float, nullable=False, default=0.0)
    influenza = Column(Float, nullable=False, default=0.0)
    uti = Column(Float, nullable=False, default=0.0)
    dizziness = Column(Float, nullable=False, default=0.0)
    fatigue = Column(Float, nullable=False, default=0.0)
    allergy = Column(Float, nullable=False, default=0.0)

    # Medications
    takes_antihypertensive = Column(Float, nullable=False, default=0.0)
    takes_diabetes_medicine = Column(Float, nullable=False, default=0.0)
    takes_inhaler = Column(Float, nullable=False, default=0.0)
    takes_blood_thinner = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile user_id={self.user_id}>"
