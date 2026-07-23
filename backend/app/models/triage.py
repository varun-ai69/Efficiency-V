from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database.session import Base

class TriageSession(Base):
    __tablename__ = "triage_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # NLU / Matching info
    matched_template_id = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    original_text = Column(String, nullable=True)
    
    # State tracking
    status = Column(String, default="in_progress", nullable=False) # in_progress, completed
    collected_features = Column(JSON, default={}, nullable=False)
    
    # Tracking question index
    current_question_index = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    user = relationship("User")

    def __repr__(self):
        return f"<TriageSession id={self.id} user_id={self.user_id} status='{self.status}'>"
