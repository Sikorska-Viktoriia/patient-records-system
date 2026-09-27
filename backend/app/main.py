from fastapi import FastAPI
from .database import engine, Base
from . import models

# Створення таблиць в БД при запусків (для швидкого старти розробки)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Інформаційна система електронних пацієнтських карт")

@app.get("/")
def read_root():
    return {"message": "Бекенд системи пацієнтських карт працює успішно!"}