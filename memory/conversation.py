from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import UserDefinedType

Base = declarative_base()

class Vector(UserDefinedType):
    def get_col_spec(self):
        return "VECTOR"
    

class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    question = Column(String)
    answer = Column(String)
    summary = Column(String)
    title = Column(String)
    embedding = Column(Vector)