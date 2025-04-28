from sqlalchemy import Column, Integer, String, Text
from vikusya.db.models.base import Base

class Emotion(Base):
    __tablename__ = "Emotions"

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100), unique=True, nullable=False)
    Description = Column(Text)
