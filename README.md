# 🚀 QuickDrop Backend

QuickDrop is a backend system built to demonstrate **real-world backend engineering concepts**, including authentication, file handling, and microservices architecture.

This project is being developed step-by-step to simulate how production backend systems are designed and scaled.

---

## 🎯 Project Goal

Build a backend system that showcases:

- Authentication systems (JWT, password hashing)
- Database integration (PostgreSQL + ORM)
- File upload and storage
- Microservices architecture principles
- Secure API design

---

## ✅ Completed Phases

### 🔹 Phase 1 — FastAPI Setup
- Initialized FastAPI application
- Created health check endpoint

### 🔹 Phase 2 — Auth Service Skeleton
- Structured auth service
- Defined API routes (`/register`, `/login`)

### 🔹 Phase 3 — Authentication System (✔ Complete)

Implemented a full authentication system:

- PostgreSQL integration
- SQLAlchemy ORM setup
- User model
- Password hashing using bcrypt
- JWT-based authentication
- Login and Register endpoints
- Protected route (`/auth/me`)
- Swagger authentication support

---

## 🧱 Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT (`python-jose`)
- **Password Hashing:** bcrypt (`passlib`)
- **API Testing:** Swagger UI

---

## 📁 Project Structure
services/
└── auth_service/
└── app/
├── api/
│ └── v1/
│ ├── auth.py
│ ├── router.py
│ └── dependencies.py
├── core/
│ ├── config.py
│ └── security.py
├── db/
│ ├── session.py
│ └── dependencies.py
├── models/
│ └── user.py
├── schemas/
│ └── auth.py
├── endpoints/
│ └── health.py
└── main.py

---

## ⚙️ Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/your-username/quickdrop-backend.git
cd quickdrop-backend

2. Create Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

3. Install Dependencies
python -m pip install \
fastapi \
uvicorn \
sqlalchemy \
psycopg2-binary \
"passlib[bcrypt]" \
"python-jose[cryptography]" \
python-dotenv \
pydantic-settings \
email-validator \
python-multipart

4. Environment Variables
Create a .env file:
AUTH_DATABASE_URL=postgresql://quickdrop_user:quickdrop_password@localhost:5432/quickdrop_auth
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

5. PostgreSQL Setup
CREATE USER quickdrop_user WITH PASSWORD 'quickdrop_password';
CREATE DATABASE quickdrop_auth OWNER quickdrop_user;
GRANT ALL PRIVILEGES ON DATABASE quickdrop_auth TO quickdrop_user;

6. Run the Server
python -m uvicorn services.auth_service.app.main:app --reload --port 8001

📌 API Endpoints
🔐 Authentication
POST /api/v1/auth/register → Register user
POST /api/v1/auth/login → Login (JSON)
POST /api/v1/auth/token → Login (Swagger OAuth)
GET /api/v1/auth/me → Get current user (Protected)
❤️ Health
GET /api/v1/health
🔑 Authentication Flow
User registers → password is hashed → stored in database
User logs in → JWT token is generated
Client sends token: Authorization: Bearer <token>
Backend validates token → fetches user → returns response

🔒 Security Features
Password hashing using bcrypt
JWT-based stateless authentication
Token expiration support
Protected routes using FastAPI dependencies
🚧 Upcoming Phases
🔵 Phase 4 — Upload Service
File upload endpoint
Local file storage
Store file metadata in database
Link uploads with authenticated users
🟣 Phase 5 — Download System
Secure file download
File streaming
Access control
🟠 Phase 6 — Microservices Communication
Service-to-service interaction
Shared contracts
API Gateway basics
🔴 Phase 7 — Production Readiness
Dockerization
Logging & monitoring
Deployment-ready architecture
💡 Learning Focus

This project demonstrates:

Backend system design
Authentication architecture
Database modeling
API development best practices
Microservices thinking
👨‍💻 Author

Harshin Mehta

⭐ Notes

This project is being built incrementally to simulate real-world backend development. Each phase introduces new concepts and improves system design.
