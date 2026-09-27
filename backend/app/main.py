from datetime import date
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Інформаційна система електронних пацієнтських карт")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
  return {"message": "Бекенд системи пацієнтських карт працює успішно!"}


@app.get("/patients/", response_model=list[schemas.PatientResponse])
def get_patients(db: Session = Depends(get_db)):
  return db.query(models.Patient).all()


@app.post(
    "/patients/",
    response_model=schemas.PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    patient_data: schemas.PatientCreate, db: Session = Depends(get_db)
):
  # Перевірка унікальності телефону в таблиці контактів
  existing_contact = (
      db.query(models.Contact)
      .filter(models.Contact.phone == patient_data.contact.phone)
      .first()
  )
  if existing_contact:
    raise HTTPException(
        status_code=400, detail="Пацієнт з таким номером телефону вже існує."
    )

  # Створення основного пацієнта
  db_patient = models.Patient(
      last_name=patient_data.last_name,
      first_name=patient_data.first_name,
      middle_name=patient_data.middle_name,
      gender=patient_data.gender,
      birth_date=patient_data.birth_date,
  )
  db.add(db_patient)
  db.commit()
  db.refresh(db_patient)

  # Створення пов'язаних записів
  db_contact = models.Contact(
      patient_id=db_patient.id,
      phone=patient_data.contact.phone,
      address=patient_data.contact.address,
  )
  db_emergency = models.EmergencyContact(
      patient_id=db_patient.id,
      name=patient_data.emergency_contact.name,
      phone=patient_data.emergency_contact.phone,
      relationship_type=patient_data.emergency_contact.relationship_type,
  )
  db_medical = models.MedicalRecord(
      patient_id=db_patient.id,
      admission_date=patient_data.medical_record.admission_date,
      admission_diagnosis=patient_data.medical_record.admission_diagnosis,
      symptoms=patient_data.medical_record.symptoms,
      status="active",
  )

  db.add_all([db_contact, db_emergency, db_medical])
  db.commit()
  db.refresh(db_patient)
  return db_patient


# Оновлення медичної карти (виписка в архів, нотатки)
@app.patch(
    "/patients/{patient_id}/medical", response_model=schemas.PatientResponse
)
def update_medical_record(
    patient_id: int,
    update_data: schemas.MedicalRecordUpdate,
    db: Session = Depends(get_db),
):
  medical = (
      db.query(models.MedicalRecord)
      .filter(models.MedicalRecord.patient_id == patient_id)
      .first()
  )
  if not medical:
    raise HTTPException(
        status_code=404, detail="Медичну карту пацієнта не знайдено"
    )

  if update_data.discharge_date:
    if update_data.discharge_date < medical.admission_date:
      raise HTTPException(
          status_code=400,
          detail="Дата виписки не може бути раніше дати госпіталізації!",
      )
    medical.discharge_date = update_data.discharge_date
    medical.status = "archived"  # Переводимо в архів

  if update_data.additional_notes is not None:
    medical.additional_notes = update_data.additional_notes

  if update_data.status:
    medical.status = update_data.status

  db.commit()
  patient = (
      db.query(models.Patient).filter(models.Patient.id == patient_id).first()
  )
  return patient