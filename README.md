# QuickDrop Backend 🚀

QuickDrop is a microservices-based backend system built with FastAPI to demonstrate real-world backend engineering concepts such as authentication, secure file upload, API Gateway routing, service separation, request tracing, and production-style observability.

The project is being developed step-by-step to simulate how backend systems are designed, secured, scaled, and prepared for production.

---

## Project Goal

The goal of QuickDrop is to build a backend system that demonstrates:

- Microservices architecture
- JWT-based authentication
- Secure password hashing
- PostgreSQL database integration
- SQLAlchemy ORM usage
- File upload and metadata storage
- User-based file ownership checks
- API Gateway routing
- Request logging and observability
- Production-readiness concepts

---

## Current Architecture

```text
Client
  ↓
Gateway Service :8002
  ├── /api/v1/auth/*    → Auth Service :8000
  └── /api/v1/uploads/* → Upload Service :8001
```

The Gateway Service acts as the single public entry point for the system.

Clients do not need to call Auth Service or Upload Service directly. They send requests to the Gateway, and the Gateway forwards those requests to the correct downstream service.

---

## Services

### Auth Service

The Auth Service is responsible for user authentication.

Responsibilities:

- User registration
- User login
- Password hashing using bcrypt
- JWT token generation
- JWT token validation
- Protected `/auth/me` endpoint
- PostgreSQL user storage

Default local port:

```text
8000
```

---

### Upload Service

The Upload Service is responsible for file upload and file access.

Responsibilities:

- Upload files
- Store files locally
- Store file metadata in PostgreSQL
- Validate JWT tokens
- Extract authenticated `user_id` from JWT
- List files owned by the authenticated user
- Download files owned by the authenticated user
- Prevent users from accessing files that do not belong to them

Default local port:

```text
8001
```

---

### Gateway Service

The Gateway Service is responsible for routing client requests to the correct internal service.

Responsibilities:

- Route `/api/v1/auth/*` requests to Auth Service
- Route `/api/v1/uploads/*` requests to Upload Service
- Forward `Authorization` headers
- Forward `X-Request-ID` headers
- Generate request IDs when missing
- Log incoming requests
- Log downstream service responses
- Log request duration
- Return clean `503 Service Unavailable` responses when downstream services are unavailable

Default local port:

```text
8002
```

---

## Tech Stack

- **Backend Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT using `python-jose`
- **Password Hashing:** bcrypt using `passlib`
- **HTTP Client:** httpx
- **Server:** Uvicorn
- **API Testing:** Swagger UI, curl
- **Language:** Python

---

## Project Structure

```text
services/
├── auth_service/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── endpoints/
│       ├── models/
│       ├── schemas/
│       └── main.py
│
├── upload_service/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       └── main.py
│
└── gateway_service/
    └── app/
        ├── api/
        ├── core/
        │   ├── config.py
        │   └── logging.py
        ├── endpoints/
        │   ├── auth_proxy.py
        │   ├── health.py
        │   └── upload_proxy.py
        └── main.py
```

---

## Completed Phases

### Phase 1: FastAPI Setup

Completed:

- Initialized FastAPI application
- Created basic health check endpoint
- Verified local server startup

---

### Phase 2: Auth Service Skeleton

Completed:

- Created Auth Service structure
- Added API router structure
- Added initial `/register` and `/login` routes
- Added health endpoint
- Confirmed routes appear in Swagger UI

---

### Phase 3: Full Authentication System

Completed:

- Integrated PostgreSQL with Auth Service
- Added SQLAlchemy ORM setup
- Created user model
- Created user schemas
- Added password hashing using bcrypt
- Added password verification
- Added JWT token generation
- Added JWT token validation
- Added login endpoint
- Added register endpoint
- Added protected `/auth/me` endpoint
- Confirmed protected routes reject missing or invalid tokens
- Confirmed Swagger authorization flow works

JWT rule:

```text
JWT sub = user_id
```

The `sub` claim stores the authenticated user's `user_id`.

---

### Phase 4: Upload Service

Completed:

- Created separate Upload Service microservice
- Added upload endpoint
- Added local file storage
- Added PostgreSQL metadata storage
- Added file metadata model
- Added JWT validation inside Upload Service
- Extracted real authenticated `user_id` from JWT
- Linked uploaded files to authenticated users
- Added file list endpoint
- Added file retrieval/download endpoint
- Added ownership check so users can only access their own files
- Confirmed missing tokens are rejected
- Confirmed invalid tokens are rejected
- Confirmed users cannot access files owned by another user

---

### Phase 5: API Gateway

Completed:

- Created separate Gateway Service
- Gateway runs on port `8002`
- Auth Service runs on port `8000`
- Upload Service runs on port `8001`
- Gateway routes `/api/v1/auth/*` to Auth Service
- Gateway routes `/api/v1/uploads/*` to Upload Service
- Confirmed register works through Gateway
- Confirmed login works through Gateway
- Confirmed `/auth/me` works through Gateway
- Confirmed file upload works through Gateway
- Confirmed file list works through Gateway
- Confirmed file download works through Gateway
- Confirmed missing token is rejected through Gateway
- Confirmed invalid token is rejected through Gateway
- Confirmed JWT `Authorization` header is forwarded correctly
- Confirmed Upload Service ownership security is preserved through Gateway

Gateway routing:

```text
Client
  ↓
Gateway Service :8002
  ├── /api/v1/auth/*    → Auth Service :8000
  └── /api/v1/uploads/* → Upload Service :8001
```

---

### Phase 6: Gateway Logging, Observability, and Production Polish

Completed:

- Added centralized Gateway logging configuration
- Added request logging middleware to Gateway Service
- Logged every incoming request
- Logged HTTP method
- Logged request path
- Logged response status code
- Logged request duration in milliseconds
- Added `X-Request-ID` support
- Preserved incoming `X-Request-ID` when provided by the client
- Generated a new request ID when the client does not provide one
- Returned `X-Request-ID` in Gateway responses
- Forwarded `X-Request-ID` to Auth Service
- Forwarded `X-Request-ID` to Upload Service
- Logged downstream Auth Service target URLs
- Logged downstream Upload Service target URLs
- Logged downstream response status codes
- Logged Auth Service unavailable errors
- Logged Upload Service unavailable errors
- Improved Swagger route summaries for Gateway proxy routes

Example Gateway log flow:

```text
Incoming request | method=GET path=/api/v1/uploads/ request_id=...
Forwarding request to Upload Service | method=GET target_url=http://127.0.0.1:8001/api/v1/uploads/ request_id=...
Upload Service responded | method=GET target_url=http://127.0.0.1:8001/api/v1/uploads/ status_code=200 request_id=...
Request completed | method=GET path=/api/v1/uploads/ status_code=200 duration_ms=... request_id=...
```

Request ID behavior:

```text
If the client sends X-Request-ID, Gateway preserves it.
If the client does not send X-Request-ID, Gateway generates one.
Gateway returns X-Request-ID in the response headers.
Gateway forwards X-Request-ID to downstream services.
```

Failure handling confirmed:

| Scenario | Gateway Response |
|---|---|
| Missing token | `403 Forbidden` |
| Invalid token | `401 Unauthorized` |
| Auth Service down | `503 Service Unavailable` |
| Upload Service down | `503 Service Unavailable` |

Example Auth Service failure response:

```json
{
  "detail": "Auth Service is unavailable"
}
```

Example Upload Service failure response:

```json
{
  "detail": "Upload Service is unavailable"
}
```

---

## Authentication Flow

```text
1. User registers through Gateway
2. Gateway forwards request to Auth Service
3. Auth Service hashes password and stores user in PostgreSQL
4. User logs in through Gateway
5. Gateway forwards login request to Auth Service
6. Auth Service verifies credentials
7. Auth Service returns JWT token
8. Client sends JWT in Authorization header
9. Gateway forwards Authorization header to downstream services
10. Upload Service validates JWT
11. Upload Service extracts user_id from JWT sub claim
12. Upload Service performs user-specific file operations
```

Authorization header format:

```text
Authorization: Bearer <access_token>
```

---

## API Endpoints

All client requests should go through the Gateway Service.

Base URL:

```text
http://127.0.0.1:8002
```

---

### Gateway Health

```text
GET /api/v1/health/
```

Example:

```bash
curl -i http://127.0.0.1:8002/api/v1/health/
```

---

### Auth Routes Through Gateway

Register user:

```text
POST /api/v1/auth/register
```

Login user:

```text
POST /api/v1/auth/login
```

Get current authenticated user:

```text
GET /api/v1/auth/me
```

---

### Upload Routes Through Gateway

Upload file:

```text
POST /api/v1/uploads/
```

List authenticated user's files:

```text
GET /api/v1/uploads/
```

Download file by id:

```text
GET /api/v1/uploads/{file_id}
```

---

## Example curl Commands

### Register

```bash
curl -i -X POST http://127.0.0.1:8002/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: register-test-001" \
  -d '{"email":"user@example.com","password":"Password123!"}'
```

---

### Login

```bash
curl -i -X POST http://127.0.0.1:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: login-test-001" \
  -d '{"email":"user@example.com","password":"Password123!"}'
```

---

### Save Token

```bash
TOKEN="paste_access_token_here"
```

---

### Get Current User

```bash
curl -i http://127.0.0.1:8002/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Request-ID: auth-me-test-001"
```

---

### Upload File

```bash
echo "QuickDrop test file" > test-file.txt
```

```bash
curl -i -X POST http://127.0.0.1:8002/api/v1/uploads/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Request-ID: upload-test-001" \
  -F "file=@test-file.txt"
```

---

### List Files

```bash
curl -i http://127.0.0.1:8002/api/v1/uploads/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Request-ID: upload-list-test-001"
```

---

### Download File

```bash
curl -i http://127.0.0.1:8002/api/v1/uploads/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Request-ID: download-test-001"
```

---

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/harshin93/quickdrop-backend.git
cd quickdrop-backend
```

---

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
python -m pip install fastapi uvicorn sqlalchemy psycopg2-binary "passlib[bcrypt]" "python-jose[cryptography]" python-dotenv pydantic-settings email-validator python-multipart httpx
```

---

### 4. Environment Variables

Create a `.env` file in the project root.

Example:

```env
AUTH_DATABASE_URL=postgresql://quickdrop_user:quickdrop_password@localhost:5432/quickdrop_auth
UPLOAD_DATABASE_URL=postgresql://quickdrop_user:quickdrop_password@localhost:5432/quickdrop_upload
JWT_SECRET_KEY=replace-with-your-own-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Do not commit real secrets to GitHub.

---

### 5. PostgreSQL Setup

Example database setup:

```sql
CREATE USER quickdrop_user WITH PASSWORD 'quickdrop_password';

CREATE DATABASE quickdrop_auth OWNER quickdrop_user;
CREATE DATABASE quickdrop_upload OWNER quickdrop_user;

GRANT ALL PRIVILEGES ON DATABASE quickdrop_auth TO quickdrop_user;
GRANT ALL PRIVILEGES ON DATABASE quickdrop_upload TO quickdrop_user;
```

---

## Running the Services Locally

Open three terminals from the project root.

### Terminal 1: Auth Service

```bash
source .venv/bin/activate
python -m uvicorn services.auth_service.app.main:app --reload --port 8000
```

---

### Terminal 2: Upload Service

```bash
source .venv/bin/activate
python -m uvicorn services.upload_service.app.main:app --reload --port 8001
```

---

### Terminal 3: Gateway Service

```bash
source .venv/bin/activate
python -m uvicorn services.gateway_service.app.main:app --reload --port 8002
```

---

## Swagger UI

Auth Service Swagger:

```text
http://127.0.0.1:8000/docs
```

Upload Service Swagger:

```text
http://127.0.0.1:8001/docs
```

Gateway Service Swagger:

```text
http://127.0.0.1:8002/docs
```

For normal client testing, use Gateway Swagger or Gateway curl commands.

---

## Security Features

Current security features:

- Password hashing with bcrypt
- JWT-based stateless authentication
- Token expiration support
- Protected routes
- Upload ownership checks
- Invalid token rejection
- Missing token rejection
- Gateway forwarding of `Authorization` header
- Gateway request tracing with `X-Request-ID`
- Downstream service failure handling

---

## Observability Features

Current observability features:

- Gateway request logging
- Request method logging
- Request path logging
- Response status code logging
- Request duration logging
- Request ID generation
- Request ID propagation
- Downstream target URL logging
- Downstream response status logging
- Downstream failure logging

These features make it easier to debug request flow across services.

---

## Current Status

QuickDrop currently has three working services:

```text
Auth Service    :8000
Upload Service  :8001
Gateway Service :8002
```

Completed:

```text
Phase 1: FastAPI setup
Phase 2: Auth Service skeleton
Phase 3: Full authentication system
Phase 4: Upload Service
Phase 5: API Gateway
Phase 6: Gateway logging, observability, and production polish
```

---

## Upcoming Phases

### Phase 7: Docker Compose / Local Orchestration

Planned:

- Run Auth Service, Upload Service, Gateway Service, and PostgreSQL using Docker Compose
- Use environment variables properly
- Confirm all services communicate inside Docker network
- Make project easier to run with one command

---

### Phase 8: Cloud/Object Storage Upgrade

Planned:

- Replace local file storage with S3-compatible storage
- Use AWS S3 or MinIO for local development
- Store only file metadata in PostgreSQL
- Keep ownership checks and JWT security working

---

### Phase 9: Testing

Planned:

- Add unit tests for Auth Service
- Add unit tests for Upload Service
- Add Gateway proxy tests
- Add integration tests for register/login/upload/download flow
- Use pytest

---

### Phase 10: Security Hardening

Planned:

- Add file size validation
- Add allowed file type validation
- Improve JWT error handling
- Add rate limiting at Gateway
- Add better CORS configuration
- Review secrets and `.env` handling

---

### Phase 11: CI/CD

Planned:

- Add GitHub Actions
- Run tests automatically on push
- Add linting and formatting checks
- Prepare for deployment pipeline

---

### Phase 12: Deployment

Planned:

- Deploy services to a cloud environment
- Use managed PostgreSQL or containerized PostgreSQL
- Configure production environment variables
- Expose only the Gateway publicly
- Keep Auth and Upload services internal

---

### Phase 13: Final Interview and Resume Polish

Planned:

- Update README with architecture diagram
- Add endpoint documentation
- Add system design explanation
- Add trade-offs section
- Add resume bullets
- Prepare interview Q&A for each service and architectural decision

---

## Interview Explanation

QuickDrop is a microservices-style backend system built with FastAPI.

The system has an Auth Service for authentication, an Upload Service for file operations, and a Gateway Service that acts as the single entry point for clients.

The Auth Service issues JWTs after login. The JWT stores the authenticated user's `user_id` in the `sub` claim. The Upload Service validates the JWT and uses the `user_id` to ensure users can only access their own uploaded files.

The Gateway forwards requests to the correct downstream service and preserves important headers like `Authorization` and `X-Request-ID`.

In Phase 6, request tracing and logging were added so every request can be tracked by method, path, status code, duration, and request ID. This makes the system easier to debug and closer to production-style backend design.

---

## Author

Harshin Mehta

---

## Notes

This project is being built incrementally to strengthen backend engineering fundamentals and demonstrate production-oriented system design.

Each phase introduces a new backend concept and improves the overall architecture.