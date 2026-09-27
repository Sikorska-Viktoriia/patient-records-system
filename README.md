Electronic Patient Records System
A modern web application for managing electronic medical patient records, developed as part of a coursework/diploma project.

Tech Stack
Frontend: Vue.js (Vite)

Backend: FastAPI (Python)

Database: PostgreSQL

Infrastructure: Docker & Docker Compose

Quick Start (Using Docker)
To run the project, ensure you have Docker and Docker Compose installed on your machine.

Clone the repository:

Bash
git clone https://github.com/Sikorska-Viktoriia/patient-records-system.git
cd patient-records-system
Run the system using Docker Compose:

Bash
docker compose up --build
Once successfully started, access the services at:

Frontend (Vue.js): http://localhost:5173

Backend & API Documentation (Swagger UI): http://localhost:8000/docs

Project Structure
Plaintext
patient-records-system/
├── backend/          # FastAPI application (models, database, routes)
├── frontend/         # Vue.js + Vite client-side application
├── docker-compose.yml # Containers orchestration configuration
└── README.md         # Project documentation
License
This project is licensed under the MIT License.
