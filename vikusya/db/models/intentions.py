from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from vikusya.db.models import base

class Intention(base):
    __tablename__ = 'Intentions'

    Id = Column(Integer, primary_key=True)
    SubjectId = Column(Integer, ForeignKey('Lexemes.Id'))
    VerbId = Column(Integer, ForeignKey('Lexemes.Id'))
    ObjectId = Column(Integer, ForeignKey('Lexemes.Id'))
    Modifier = Column(Text)
    CreatedAt = Column(TIMESTAMP)
