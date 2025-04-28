from sqlalchemy import Column, Integer, ForeignKey, Float
from vikusya.db.models import base

class LexemeEmotionWeight(base):
    __tablename__ = 'LexemeEmotionWeights'

    LexemeId = Column(Integer, ForeignKey('Lexemes.Id'), primary_key=True)
    EmotionId = Column(Integer, ForeignKey('Emotions.Id'), primary_key=True)
    Weight = Column(Float, nullable=False)