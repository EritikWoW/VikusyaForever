from sqlalchemy import Column, Integer, Boolean, String
from vikusya.db.models.base import Base

class VerbRequirement(Base):
    __tablename__ = 'VerbRequirements'

    Id = Column(Integer, primary_key=True)
    Verb = Column(String(255), unique=True, nullable=False)
    RequiresPreposition = Column(Boolean, default=False)
    Preposition = Column(String(50))
    RequiredCase = Column(String(50))