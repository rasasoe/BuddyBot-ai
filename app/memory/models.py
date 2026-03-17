from sqlalchemy import Column, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Memory(Base):
    __tablename__ = "memory"
    key = Column(String, primary_key=True)
    value = Column(Text)