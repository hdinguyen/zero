from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Debug(Base):
    __tablename__ = "debug"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    conversation_id = Column(Integer)
    reasoning = Column(String)
    trajectory = Column(String)
    human_feedback = Column(String)