from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .database import Base


class Patient(Base):
  __tablename__ = 'patients'

  id = Column(Integer, primary_key=True, index=True)
  last_name = Column(String, nullable=False)
  first_name = Column(String, nullable=False)
  middle_name = Column(String, nullable=True)
  gender = Column(String, nullable=False)
  birth_date = Column(Date, nullable=False)

  contact = relationship(
      'Contact', back_populates='patient', uselist=False, cascade='all, delete'
  )
  emergency_contact = relationship(
      'EmergencyContact',
      back_populates='patient',
      uselist=False,
      cascade='all, delete',
  )
  medical_record = relationship(
      'MedicalRecord',
      back_populates='patient',
      uselist=False,
      cascade='all, delete',
  )


class Contact(Base):
  __tablename__ = 'contacts'

  id = Column(Integer, primary_key=True, index=True)
  patient_id = Column(Integer, ForeignKey('patients.id'), unique=True)
  phone = Column(String, unique=True, index=True, nullable=False)
  address = Column(String, nullable=True)

  patient = relationship('Patient', back_populates='contact')


class EmergencyContact(Base):
  __tablename__ = 'emergency_contacts'

  id = Column(Integer, primary_key=True, index=True)
  patient_id = Column(Integer, ForeignKey('patients.id'), unique=True)
  name = Column(String, nullable=False)
  phone = Column(String, nullable=False)
  relationship_type = Column(String, nullable=True)

  patient = relationship('Patient', back_populates='emergency_contact')


class MedicalRecord(Base):
  __tablename__ = 'medical_records'

  id = Column(Integer, primary_key=True, index=True)
  patient_id = Column(Integer, ForeignKey('patients.id'), unique=True)
  admission_date = Column(Date, nullable=False)
  admission_diagnosis = Column(Text, nullable=False)
  symptoms = Column(Text, nullable=True)

  # Додаткові медичні дані
  blood_type = Column(String, nullable=True)  # Група крові (напр. A(II)+)
  allergies = Column(Text, nullable=True)  # Алергії
  contraindications = Column(Text, nullable=True)  # Протипоказання

  discharge_date = Column(Date, nullable=True)
  status = Column(String, default='active')  # 'active' або 'archived'
  additional_notes = Column(Text, nullable=True)

  patient = relationship('Patient', back_populates='medical_record')