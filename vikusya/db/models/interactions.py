from sqlalchemy import Column, Integer, Text, String, TIMESTAMP
from vikusya.db.models.base import Base

class Interaction(Base):
    __tablename__ = 'Interactions'

    Id = Column(Integer, primary_key=True)
    Timestamp = Column(TIMESTAMP)
    UserInput = Column(Text, nullable=False)
    VikusyaAnswer = Column(Text, nullable=False)
    Tags = Column(String(255))
    Rating = Column(Integer)
    Notes = Column(Text)