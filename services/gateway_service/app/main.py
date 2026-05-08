import sys
import time
import uuid

from fastapi import FastAPI, Request

from services.gateway_service.app.api.v1.router import api_router
from services.gateway_service.app.core.config import settings
from services.gateway_service.app.core.logging import configure_logging


configure_logging()


def gateway_log(message: str) -> None:
    print(message, file=sys.stdout, flush=True)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


@app.middleware("http")
async def log_gateway_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    start_time = time.perf_counter()

    gateway_log(
        f"Incoming request | method={request.method} path={request.url.path} request_id={request_id}"
    )

    try:
        response = await call_next(request)

    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000

        gateway_log(
            f"Request failed | method={request.method} path={request.url.path} "
            f"status_code=500 duration_ms={duration_ms:.2f} request_id={request_id}"
        )

        raise

    duration_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id

    gateway_log(
        f"Request completed | method={request.method} path={request.url.path} "
        f"status_code={response.status_code} duration_ms={duration_ms:.2f} request_id={request_id}"
    )

    return response


app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    return {
        "message": "QuickDrop Gateway Service is running"
    }
