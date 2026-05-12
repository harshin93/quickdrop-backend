# QuickDrop Backend

QuickDrop is a microservices-style backend system built with **FastAPI**. It demonstrates production-oriented backend engineering concepts such as service separation, JWT authentication, secure password hashing, API Gateway routing, PostgreSQL persistence, S3-compatible object storage, request tracing, structured logging, Docker Compose orchestration, and automated integration testing.

The project is being built incrementally in phases to simulate how a backend system evolves from a simple API into a more realistic distributed backend.

---

## Project Goal

The goal of QuickDrop is to build an interview-ready backend system that demonstrates:

* Microservices-style architecture
* API Gateway routing
* JWT-based authentication
* Secure password hashing with bcrypt
* PostgreSQL database integration
* SQLAlchemy ORM usage
* Authenticated file upload, listing, and download
* User-based file ownership checks
* S3-compatible object storage using MinIO
* Request tracing with `X-Request-ID`
* Production-style logging and error handling
* Docker Compose local orchestration
* Automated integration testing with Pytest

---

## Current Architecture

```text
Client
  |
  v
Gateway Service :8002
  |
  |-- /api/v1/auth/*    --> Auth Service :8000 --> Auth PostgreSQL :5433
  |
  |-- /api/v1/uploads/* --> Upload Service :8001 --> Upload PostgreSQL :5434
                                           |
                                           v
                                      MinIO Object Storage :9000
```

The **Gateway Service** is the public entry point for the system. Clients call the Gateway, and the Gateway forwards requests to the correct internal service.

The **Auth Service** owns user registration, login, password hashing, JWT creation, and protected user profile access.

The **Upload Service** owns authenticated file upload, metadata persistence, MinIO object storage, file listing, file download, and ownership checks.

---

## Active Services

### Gateway Service

The Gateway Service routes external client requests to internal services.

Responsibilities:

* Route `/api/v1/auth/*` requests to Auth Service
* Route `/api/v1/uploads/*` requests to Upload Service
* Forward `Authorization` headers
* Forward and return `X-Request-ID` headers
* Generate a request ID when the client does not provide one
* Log incoming requests
* Log downstream service calls
* Log downstream response status codes
* Log request duration
* Return clean `503 Service Unavailable` responses when downstream services are unavailable

Default local port:

```text
8002
```

---

### Auth Service

The Auth Service is responsible for authentication and user identity.

Responsibilities:

* Register users
* Hash passwords using bcrypt
* Store user records in PostgreSQL
* Login users
* Verify passwords
* Generate JWT access tokens
* Store the authenticated user ID in the JWT `sub` claim
* Validate JWTs for protected routes
* Expose protected `/auth/me` endpoint

Default local port:

```text
8000
```

Database port exposed on host:

```text
5433
```

---

### Upload Service

The Upload Service is responsible for authenticated file operations.

Responsibilities:

* Validate JWT Bearer tokens
* Extract authenticated `user_id` from JWT `sub` claim
* Upload files to MinIO object storage
* Store file metadata in PostgreSQL
* Store MinIO object keys in `FileMetadata.file_path`
* List files owned by the authenticated user
* Download files owned by the authenticated user
* Prevent users from accessing files that do not belong to them

Default local port:

```text
8001
```

Database port exposed on host:

```text
5434
```

MinIO API port:

```text
9000
```

MinIO console port:

```text
9001
```

Default MinIO bucket:

```text
quickdrop-uploads
```

Object key format:

```text
users/{user_id}/{uuid}-{filename}
```

---

## Tech Stack

* **Language:** Python
* **Framework:** FastAPI
* **Server:** Uvicorn
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Authentication:** JWT with `python-jose`
* **Password Hashing:** bcrypt with `passlib`
* **Object Storage:** MinIO using `boto3`
* **HTTP Client:** httpx
* **Testing:** Pytest
* **Containerization:** Docker and Docker Compose
* **Validation/Settings:** Pydantic and pydantic-settings

---

## Project Structure

```text
services/
├── auth_service/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── endpoints/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── upload_service/
│   └── app/
│       ├── api/
│       ├── core/
│       │   ├── config.py
│       │   ├── logging.py
│       │   ├── security.py
│       │   └── storage.py
│       ├── db/
│       ├── models/
│       ├── schemas/
│       └── main.py
│
├── gateway_service/
│   └── app/
│       ├── api/
│       ├── core/
│       │   ├── config.py
│       │   └── logging.py
│       ├── endpoints/
│       │   ├── auth_proxy.py
│       │   ├── health.py
│       │   └── upload_proxy.py
│       └── main.py
│
tests/
├── test_auth_errors.py
├── test_auth_flow.py
├── test_gateway_flow.py
├── test_health.py
├── test_upload_errors.py
└── test_upload_flow.py
```

---

## API Gateway Routes

All normal client requests should go through the Gateway Service.

Base URL:

```text
http://127.0.0.1:8002
```

### Health

```http
GET /api/v1/health/
```

### Authentication

```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### File Uploads

```http
POST /api/v1/uploads/
GET  /api/v1/uploads/
GET  /api/v1/uploads/{file_id}
```

---

## Authentication Flow

```text
1. Client registers through Gateway.
2. Gateway forwards request to Auth Service.
3. Auth Service hashes the password and stores the user in PostgreSQL.
4. Client logs in through Gateway.
5. Auth Service verifies the password.
6. Auth Service creates a JWT access token.
7. JWT stores user_id in the sub claim.
8. Client sends the JWT in the Authorization header.
9. Gateway forwards the Authorization header to downstream services.
10. Upload Service validates the JWT.
11. Upload Service extracts user_id from the JWT sub claim.
12. Upload Service performs user-specific file operations.
```

Authorization header format:

```http
Authorization: Bearer <access_token>
```

---

## File Upload Flow

```text
1. Authenticated client uploads file through Gateway.
2. Gateway forwards multipart request to Upload Service.
3. Upload Service validates JWT.
4. Upload Service extracts user_id from JWT sub claim.
5. Upload Service creates a MinIO object key.
6. Upload Service uploads file bytes to MinIO.
7. Upload Service stores metadata in PostgreSQL.
8. Upload Service stores the MinIO object key in file_path.
9. User can list and download only their own files.
```

Example object key:

```text
users/12/550e8400-e29b-41d4-a716-446655440000-example.txt
```

---

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/harshin93/quickdrop-backend.git
cd quickdrop-backend
```

### 2. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install runtime dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Install development dependencies

```bash
python -m pip install -r requirements-dev.txt
```

---

## Running with Docker Compose

The recommended way to run the full local system is Docker Compose.

Start all services:

```bash
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

View only Gateway logs:

```bash
docker compose logs -f gateway_service
```

Stop services:

```bash
docker compose down
```

Stop services and remove volumes:

```bash
docker compose down -v
```

Use `docker compose down -v` carefully because it removes local PostgreSQL and MinIO data volumes.

---

## Docker Compose Services

| Service               | Container                       |      Host Port | Purpose                            |
| --------------------- | ------------------------------- | -------------: | ---------------------------------- |
| `gateway_service`     | `quickdrop-gateway-service`     |         `8002` | Public API entry point             |
| `auth_service`        | `quickdrop-auth-service`        |         `8000` | Authentication and JWT issuance    |
| `upload_service`      | `quickdrop-upload-service`      |         `8001` | File upload/list/download          |
| `auth_postgres`       | `quickdrop-auth-postgres`       |         `5433` | Auth database                      |
| `upload_postgres`     | `quickdrop-upload-postgres`     |         `5434` | Upload metadata database           |
| `minio`               | `quickdrop-minio`               | `9000`, `9001` | Object storage and console         |
| `minio_create_bucket` | `quickdrop-minio-create-bucket` |            N/A | Creates `quickdrop-uploads` bucket |

---

## MinIO

MinIO is used as a local S3-compatible object storage service.

Default local endpoints:

```text
MinIO API:     http://127.0.0.1:9000
MinIO Console: http://127.0.0.1:9001
```

Default bucket:

```text
quickdrop-uploads
```

The Upload Service stores file bytes in MinIO and stores only metadata plus the object key in PostgreSQL.

---

## Example curl Commands

### Gateway health check

```bash
curl -i http://127.0.0.1:8002/api/v1/health/
```

### Register user

```bash
curl -i -X POST http://127.0.0.1:8002/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: register-test-001" \
  -d '{"email":"user@example.com","password":"Password123!"}'
```

### Login user

```bash
curl -i -X POST http://127.0.0.1:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: login-test-001" \
  -d '{"email":"user@example.com","password":"Password123!"}'
```

### Save token

```bash
TOKEN="paste_access_token_here"
```

### Get current user

```bash
curl -i http://127.0.0.1:8002/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Request-ID: auth-me-test-001"
```

### Upload file

```bash
echo "QuickDrop test file" > test-file.txt

curl -i -X POST http://127.0.0.1:8002/api/v1/uploads/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Request-ID: upload-test-001" \
  -F "file=@test-file.txt"
```

### List files

```bash
curl -i http://127.0.0.1:8002/api/v1/uploads/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Request-ID: upload-list-test-001"
```

### Download file

```bash
curl -L -X GET "http://127.0.0.1:8002/api/v1/uploads/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Request-ID: download-test-001" \
  -o downloaded-file.txt
```

---

## Automated Testing

QuickDrop uses **Pytest** for automated integration testing.

The current test suite verifies real running services rather than only testing isolated functions. These tests require Docker Compose to be running because they exercise the Auth Service, Upload Service, Gateway Service, PostgreSQL databases, and MinIO together.

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Start the local stack:

```bash
docker compose up -d
```

Run all tests:

```bash
python -m pytest tests -v
```

Expected current result:

```text
16 passed
```

Current test coverage:

* Auth Service health check
* Upload Service health check
* Gateway Service health check
* User registration
* User login
* JWT creation
* Protected `/auth/me` access
* Duplicate registration rejection
* Wrong password rejection
* Missing token rejection
* Invalid token rejection
* Authenticated file upload
* File metadata persistence in PostgreSQL
* File object storage through MinIO
* File listing
* File download byte verification
* Non-existing file download rejection
* Cross-user file ownership protection
* Gateway auth routing
* Gateway upload/list/download routing
* Gateway missing-token behavior
* Gateway `X-Request-ID` behavior

These are integration tests because they verify that multiple system components work together correctly: HTTP routing, JWT authentication, database persistence, object storage, and Gateway forwarding.

---

## Security Features

Current security features:

* Password hashing with bcrypt
* JWT-based stateless authentication
* JWT expiration support
* Protected routes
* Bearer token validation
* Invalid token rejection
* Missing token rejection
* Upload ownership checks
* Cross-user file access prevention
* Gateway forwarding of `Authorization` header
* Gateway request tracing with `X-Request-ID`
* Downstream service failure handling

---

## Observability Features

Current observability features:

* Gateway request logging
* Request method logging
* Request path logging
* Response status code logging
* Request duration logging
* Request ID generation
* Request ID propagation
* Downstream target URL logging
* Downstream response status logging
* Downstream failure logging

Example Gateway log flow:

```text
Incoming request | method=GET path=/api/v1/uploads/ request_id=...
Forwarding request to Upload Service | method=GET target_url=http://upload_service:8001/api/v1/uploads/ request_id=...
Upload Service responded | method=GET target_url=http://upload_service:8001/api/v1/uploads/ status_code=200 request_id=...
Request completed | method=GET path=/api/v1/uploads/ status_code=200 duration_ms=... request_id=...
```

Request ID behavior:

```text
If the client sends X-Request-ID, Gateway preserves it.
If the client does not send X-Request-ID, Gateway generates one.
Gateway returns X-Request-ID in the response headers.
Gateway forwards X-Request-ID to downstream services.
```

---

## Completed Phases

### Phase 1: FastAPI Base Setup

Completed:

* Initialized FastAPI application
* Created basic health check endpoint
* Verified local server startup

### Phase 2: Auth Service Skeleton

Completed:

* Created Auth Service structure
* Added router structure
* Added initial auth routes
* Added health endpoint
* Confirmed routes in Swagger UI

### Phase 3: Full Authentication System

Completed:

* Integrated PostgreSQL with Auth Service
* Added SQLAlchemy ORM setup
* Created user model and schemas
* Added password hashing using bcrypt
* Added password verification
* Added JWT creation and validation
* Added register endpoint
* Added login endpoint
* Added protected `/auth/me` endpoint
* Confirmed protected routes reject missing or invalid tokens

JWT rule:

```text
JWT sub = user_id
```

### Phase 4: Upload Service

Completed:

* Created Upload Service microservice
* Added upload endpoint
* Added file metadata model
* Added PostgreSQL metadata storage
* Added JWT validation inside Upload Service
* Extracted authenticated `user_id` from JWT
* Linked uploaded files to authenticated users
* Added file list endpoint
* Added file download endpoint
* Added ownership checks
* Confirmed users cannot access files owned by another user

### Phase 5: API Gateway

Completed:

* Created Gateway Service
* Routed `/api/v1/auth/*` to Auth Service
* Routed `/api/v1/uploads/*` to Upload Service
* Forwarded Authorization headers
* Confirmed register/login/me works through Gateway
* Confirmed upload/list/download works through Gateway
* Confirmed Upload Service ownership security is preserved through Gateway

### Phase 6: Gateway Logging and Observability

Completed:

* Added centralized Gateway logging configuration
* Added Gateway request logging middleware
* Added `X-Request-ID` support
* Preserved incoming request IDs
* Generated request IDs when missing
* Returned request IDs in responses
* Forwarded request IDs downstream
* Logged method, path, status code, duration, and downstream responses
* Added clean downstream service unavailable handling

### Phase 7: Docker Compose Local Orchestration

Completed:

* Added Docker Compose orchestration
* Added Auth Service container
* Added Upload Service container
* Added Gateway Service container
* Added separate Auth PostgreSQL container
* Added separate Upload PostgreSQL container
* Configured internal Docker networking
* Configured Gateway to call services by Docker service name
* Verified core flows through Docker Compose

### Phase 8: MinIO Object Storage

Completed:

* Added MinIO container
* Added MinIO bucket initialization container
* Created `quickdrop-uploads` bucket
* Replaced local upload file storage with object storage
* Added `boto3` storage integration
* Stored object keys in PostgreSQL metadata
* Verified upload/list/download through Gateway using MinIO
* Removed reliance on local upload volume for active storage

### Phase 9: Automated Testing Setup

Completed:

* Added Pytest development dependency
* Added health-check integration tests
* Added Auth Service happy-path tests
* Added Auth Service error-path tests
* Added Upload Service happy-path tests
* Added Upload Service error/security tests
* Added Gateway routing tests
* Verified MinIO-backed upload/list/download flow through tests
* Verified cross-user file ownership protection through tests
* Verified Gateway `X-Request-ID` behavior through tests
* Confirmed full suite passes with 16 tests

---

## Upcoming Phases

### Phase 10: Security Hardening

Planned:

* Add file size validation
* Add allowed file type validation
* Improve JWT error consistency
* Add rate limiting at Gateway
* Add stricter CORS configuration
* Review secrets and `.env` handling

### Phase 11: CI/CD

Planned:

* Add GitHub Actions workflow
* Run tests automatically on push or pull request
* Add linting checks
* Add formatting checks
* Prepare deployment pipeline foundation

### Phase 12: Deployment

Planned:

* Deploy services to a cloud environment
* Use managed PostgreSQL or containerized PostgreSQL
* Configure production environment variables
* Expose only the Gateway publicly
* Keep Auth and Upload services internal

### Phase 13: Final Interview and Resume Polish

Planned:

* Add architecture diagram
* Add system design trade-offs
* Add scaling discussion
* Add failure-mode discussion
* Add resume bullets
* Prepare interview Q&A for each service and architectural decision

---

## Interview Explanation

QuickDrop is a microservices-style backend system built with FastAPI.

The system has an Auth Service for authentication, an Upload Service for file operations, and a Gateway Service that acts as the single public entry point for clients.

The Auth Service stores users in PostgreSQL, hashes passwords with bcrypt, and issues JWT access tokens after login. The JWT stores the authenticated user's `user_id` in the `sub` claim.

The Upload Service validates JWTs, extracts the `user_id`, stores uploaded file bytes in MinIO object storage, and stores file metadata in PostgreSQL. File access is protected with ownership checks, so users can only list or download their own files.

The Gateway forwards requests to the correct downstream service and preserves important headers like `Authorization` and `X-Request-ID`. It also logs request method, path, status code, duration, request ID, downstream target URL, and downstream response status.

In Phase 9, automated integration tests were added using Pytest. These tests verify health checks, authentication, protected routes, upload/list/download behavior, MinIO object storage flow, ownership protection, and Gateway routing. In Phase 10, the backend was hardened with upload size limits, content-type allowlisting, filename sanitization, consistent JWT errors, strict Gateway CORS, security response headers, secret/config documentation, and Gateway request-size protection. The test suite now verifies these security controls so regressions can be caught automatically instead of relying only on manual curl or Swagger testing.

---

## Current Status

QuickDrop currently has a working Docker Compose-based local backend with:

```text
Auth Service       :8000
Upload Service     :8001
Gateway Service    :8002
Auth PostgreSQL    :5433
Upload PostgreSQL  :5434
MinIO API          :9000
MinIO Console      :9001
```

Current test result:

```text
16 passed
```

---

## Author

Harshin Mehta

---

## Notes

This project is being built incrementally to strengthen backend engineering fundamentals and demonstrate production-oriented system design.

Each phase introduces a new backend concept and improves the overall architecture.
