from datetime import date
from pydantic import BaseModel, Field, field_validator


class ContactCreate(BaseModel):
  phone: str
  address: str | None = None


class EmergencyContactCreate(BaseModel):
  name: str
  phone: str
  relationship_type: str | None = None


class MedicalRecordCreate(BaseModel):
  admission_date: date
  admission_diagnosis: str
  symptoms: str | None = None

  @field_validator('admission_date')
  def validate_admission(cls, v):
    if v > date.today():
      raise ValueError('Дата госпіталізації не може бути в майбутньому!')
    return v


# Схема для відповіді клієнту, що містить повні медичні дані, статус та дату виписки
class MedicalRecordResponse(BaseModel):
  admission_date: date
  admission_diagnosis: str
  symptoms: str | None = None
  blood_type: str | None = None
  allergies: str | None = None
  contraindications: str | None = None
  discharge_date: date | None = None
  status: str
  additional_notes: str | None = None

  class Config:
    from_attributes = True


class PatientCreate(BaseModel):
  last_name: str
  first_name: str
  middle_name: str | None = None
  gender: str
  birth_date: date
  contact: ContactCreate
  emergency_contact: EmergencyContactCreate
  medical_record: MedicalRecordCreate

  @field_validator('birth_date')
  def validate_birth_date(cls, v):
    if v > date.today():
      raise ValueError('Дата народження не може бути в майбутньому!')
    if v.year < 1900:
      raise ValueError('Дата народження занадто стара.')
    return v


class MedicalRecordUpdate(BaseModel):
  blood_type: str | None = None
  allergies: str | None = None
  contraindications: str | None = None
  discharge_date: date | None = None
  additional_notes: str | None = None
  status: str | None = None


class PatientResponse(BaseModel):
  id: int
  last_name: str
  first_name: str
  middle_name: str | None = None
  gender: str
  birth_date: date
  contact: ContactCreate
  emergency_contact: EmergencyContactCreate
  medical_record: MedicalRecordResponse | None = None

  class Config:
    from_attributes = True