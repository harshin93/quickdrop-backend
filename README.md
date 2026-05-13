# QuickDrop Backend

QuickDrop is a microservices-style backend system built with **FastAPI**. It demonstrates production-oriented backend engineering concepts such as service separation, JWT authentication, secure password hashing, API Gateway routing, PostgreSQL persistence, S3-compatible object storage, request tracing, structured logging, Docker Compose orchestration, automated integration testing, security hardening, and Docker Compose-based CI/CD with GitHub Actions.

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
* Security hardening for file uploads, JWT errors, CORS, and response headers
* CI/CD readiness using GitHub Actions

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

The **Upload Service** owns authenticated file upload, metadata persistence, MinIO object storage, file listing, file download, file validation, filename sanitization, and ownership checks.

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
* Enforce strict CORS rules
* Add security response headers
* Reject oversized upload requests before forwarding them downstream

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
* Return consistent invalid-token errors
* Expose protected `/auth/me` endpoint

Default local port:

```text
8000
```

Database port exposed on host:

```text
5433
```

Health endpoint:

```http
GET /api/v1/health
```

---

### Upload Service

The Upload Service is responsible for authenticated file operations.

Responsibilities:

* Validate JWT Bearer tokens
* Return consistent invalid-token errors
* Extract authenticated `user_id` from JWT `sub` claim
* Validate upload file size
* Validate allowed upload content types
* Sanitize unsafe filenames
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

Health endpoint:

```http
GET /health
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
* **CI/CD:** GitHub Actions
* **Validation/Settings:** Pydantic and pydantic-settings

---

## Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
├── requirements.txt
├── requirements-runtime.txt
├── requirements-dev.txt
├── README.md
├── services/
│   ├── auth_service/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── db/
│   │   │   ├── endpoints/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── upload_service/
│   │   └── app/
│   │       ├── api/
│   │       ├── core/
│   │       │   ├── config.py
│   │       │   ├── logging.py
│   │       │   ├── security.py
│   │       │   └── storage.py
│   │       ├── db/
│   │       ├── models/
│   │       ├── schemas/
│   │       └── main.py
│   │
│   └── gateway_service/
│       └── app/
│           ├── api/
│           ├── core/
│           │   ├── config.py
│           │   └── logging.py
│           ├── endpoints/
│           │   ├── auth_proxy.py
│           │   ├── health.py
│           │   └── upload_proxy.py
│           └── main.py
│
└── tests/
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

JWT rule:

```text
JWT sub = user_id
```

---

## File Upload Flow

```text
1. Authenticated client uploads a file through Gateway.
2. Gateway checks request size before forwarding.
3. Gateway forwards the multipart request to Upload Service.
4. Upload Service validates the JWT.
5. Upload Service extracts user_id from JWT sub claim.
6. Upload Service validates file size.
7. Upload Service validates content type.
8. Upload Service sanitizes the original filename.
9. Upload Service creates a MinIO object key.
10. Upload Service uploads file bytes to MinIO.
11. Upload Service stores metadata in PostgreSQL.
12. Upload Service stores the MinIO object key in file_path.
13. User can list and download only their own files.
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
python -m pip install -r requirements-runtime.txt
```

### 4. Install development dependencies

```bash
python -m pip install -r requirements-dev.txt
```

---

## Environment Configuration

The project includes an example environment file:

```text
.env.example
```

This file documents expected configuration values such as JWT settings, database URLs, service URLs, CORS settings, upload limits, and MinIO/S3 settings.

Important rule:

```text
Do not commit real secrets to Git.
```

For local development, create a `.env` file when needed:

```bash
cp .env.example .env
```

Then update values locally.

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

| Service               | Container                       | Host Port    | Purpose                         |
| --------------------- | ------------------------------- | ------------ | ------------------------------- |
| `gateway_service`     | `quickdrop-gateway-service`     | `8002`       | Public API entry point          |
| `auth_service`        | `quickdrop-auth-service`        | `8000`       | Authentication and JWT issuance |
| `upload_service`      | `quickdrop-upload-service`      | `8001`       | File upload/list/download       |
| `auth_postgres`       | `quickdrop-auth-postgres`       | `5433`       | Auth database                   |
| `upload_postgres`     | `quickdrop-upload-postgres`     | `5434`       | Upload metadata database        |
| `minio`               | `quickdrop-minio`               | `9000, 9001` | Object storage and console      |
| `minio_create_bucket` | `quickdrop-minio-create-bucket` | N/A          | Creates `quickdrop-uploads`     |

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

Check running containers:

```bash
docker compose ps
```

Run all tests:

```bash
python -m pytest tests -v
```

Expected current result:

```text
23 passed
```

Current test coverage includes:

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
* Gateway configured CORS origin behavior
* Gateway blocked CORS origin behavior
* Gateway security response headers
* Gateway oversized upload request rejection
* Gateway `X-Request-ID` behavior
* Upload file size validation
* Upload content-type validation
* Safer filename sanitization

These are integration tests because they verify that multiple system components work together correctly: HTTP routing, JWT authentication, database persistence, object storage, security validation, and Gateway forwarding.

---

## CI/CD

QuickDrop uses **GitHub Actions** for continuous integration.

The CI workflow is defined in:

```text
.github/workflows/ci.yml
```

The workflow runs automatically on:

```text
push to main
pull_request to main
```

The CI pipeline performs these steps:

```text
1. Check out the repository
2. Set up Python 3.11
3. Install runtime and development dependencies
4. Validate the Docker Compose configuration
5. Build Docker images
6. Start the full Docker Compose stack
7. Show running containers
8. Wait for Auth, Upload, and Gateway readiness endpoints
9. Run the Pytest integration suite
10. Print Docker Compose logs on failure
11. Shut down the Docker Compose stack
```

CI readiness endpoints:

```text
Auth Service:    http://127.0.0.1:8000/api/v1/health
Upload Service:  http://127.0.0.1:8001/health
Gateway Service: http://127.0.0.1:8002/api/v1/health/
```

This CI approach is intentionally Docker Compose-based because the tests are integration tests. They require real containers for the Auth Service, Upload Service, Gateway Service, PostgreSQL databases, and MinIO object storage.

Interview explanation:

```text
The CI pipeline starts the same Docker Compose environment used in local development, waits for services to become reachable, then runs the full Pytest integration suite. This validates not only Python code, but also container builds, service startup, database connectivity, MinIO connectivity, JWT authentication, Gateway routing, security checks, and inter-service communication.
```

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
* Upload file size validation
* Upload content-type allowlisting
* Safer filename sanitization
* Consistent invalid JWT error responses
* Strict Gateway CORS configuration
* Gateway security response headers
* Gateway request-size protection before forwarding uploads
* Secret and configuration documentation through `.env.example`
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

### Phase 10: Security Hardening

Completed:

* Added upload file size validation
* Added allowed upload content-type validation
* Added safer filename sanitization
* Added consistent invalid JWT error responses across Auth Service and Upload Service
* Added strict Gateway CORS configuration
* Added Gateway security response headers
* Added secret/config documentation through `.env.example`
* Added Gateway request-size protection before forwarding uploads
* Confirmed full suite passes with 23 tests

### Phase 11: CI/CD and Deployment Readiness

Completed:

* Added GitHub Actions workflow
* Configured CI to run on push and pull request to `main`
* Installed runtime and development dependencies in CI
* Added Docker Compose config validation in CI
* Added Docker image build validation in CI
* Started the full Docker Compose stack in CI
* Added readiness checks for Auth, Upload, and Gateway services
* Ran the full Pytest integration suite in CI
* Added Docker Compose logs on failure for easier debugging
* Added automatic Docker Compose cleanup after CI runs
* Fixed CI readiness check to use the correct Upload Service `/health` endpoint
* Confirmed GitHub Actions workflow passes

---

## Upcoming Phases

### Phase 12: Deployment

Planned:

* Prepare deployment strategy
* Decide target deployment platform
* Configure production-style environment variables
* Expose only the Gateway publicly
* Keep Auth and Upload services internal where practical
* Decide database and object storage strategy for deployment
* Document deployment trade-offs

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

The Upload Service validates JWTs, extracts the `user_id`, validates upload size and content type, sanitizes filenames, stores uploaded file bytes in MinIO object storage, and stores file metadata in PostgreSQL. File access is protected with ownership checks, so users can only list or download their own files.

The Gateway forwards requests to the correct downstream service and preserves important headers like `Authorization` and `X-Request-ID`. It also logs request method, path, status code, duration, request ID, downstream target URL, and downstream response status. The Gateway also applies strict CORS configuration, security response headers, and request-size protection before forwarding uploads.

The backend includes automated integration tests using Pytest. These tests verify health checks, authentication, protected routes, upload/list/download behavior, MinIO object storage flow, ownership protection, Gateway routing, CORS behavior, security headers, upload validation, and request-size protection.

The project also includes a Docker Compose-based GitHub Actions CI pipeline. On every push or pull request to `main`, CI builds the Docker images, starts the full backend stack, waits for service readiness, runs the 23-test integration suite, prints logs on failure, and shuts the stack down cleanly.

---

## Current Status

QuickDrop currently has a working Docker Compose-based local backend with:

```text
Auth Service        :8000
Upload Service      :8001
Gateway Service     :8002
Auth PostgreSQL     :5433
Upload PostgreSQL   :5434
MinIO API           :9000
MinIO Console       :9001
```

Current local test result:

```text
23 passed
```

Current CI/CD status:

```text
GitHub Actions Docker Compose CI passing
```

---

## Author

Harshin Mehta

---

## Notes

This project is being built incrementally to strengthen backend engineering fundamentals and demonstrate production-oriented system design.

Each phase introduces a new backend concept and improves the overall architecture.