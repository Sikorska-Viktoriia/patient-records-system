from sqlalchemy import Column, Integer, String, Text, Date
from .database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    birth_date = Column(Date, nullable=False)
    phone = Column(String, unique=True, index=True)
    medical_history = Column(Text, nullable=True)