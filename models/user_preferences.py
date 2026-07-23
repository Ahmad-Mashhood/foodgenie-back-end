from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    diet_type = Column(String(50), default="any")
    max_calories = Column(Integer, nullable=True, default=2000)
    allergies = Column(String(255), nullable=True)
    preferred_cuisine = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="preferences")
