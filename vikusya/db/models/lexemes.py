from sqlalchemy import Column, Integer, String, Boolean, Text
from vikusya.db.models import base

class Lexeme(base):
    __tablename__ = 'Lexemes'

    Id = Column(Integer, primary_key=True)
    Word = Column(String(255), unique=True, nullable=False)
    PartOfSpeech = Column(String(50))
    Gender = Column(String(20))
    Animate = Column(Boolean)
    Description = Column(Text)
    IsScreenshotTrigger = Column(Boolean, default=False)