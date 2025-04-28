from sqlalchemy import Column, Integer, String, Text
from vikusya.db.models import base

class Emotion(base):
    __tablename__ = "Emotions"

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100), unique=True, nullable=False)
    Description = Column(Text)
