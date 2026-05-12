import httpx
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import Response

from services.gateway_service.app.core.config import settings
from services.gateway_service.app.core.logging import gateway_logger

router = APIRouter(prefix="/uploads", tags=["Upload Proxy"])


def clean_request_headers(headers: dict) -> dict:
    headers.pop("host", None)
    headers.pop("content-length", None)
    return headers


def clean_response_headers(headers: dict) -> dict:
    allowed_headers = {}

    for key, value in headers.items():
        lower_key = key.lower()

        if lower_key in [
            "content-type",
            "content-disposition",
            "cache-control",
        ]:
            allowed_headers[key] = value

    return allowed_headers


async def forward_upload_request(request: Request, path: str = ""):
    if path:
        target_url = f"{settings.upload_service_url}/api/v1/uploads/{path}"
    else:
        target_url = f"{settings.upload_service_url}/api/v1/uploads/"

    request_id = getattr(
        request.state,
        "request_id",
        request.headers.get("X-Request-ID", "unknown"),
    )

    content_length = request.headers.get("content-length")

    if request.method in {"POST", "PUT"} and content_length is not None:
        try:
            request_size = int(content_length)
        except ValueError:
            gateway_logger.warning(
                "Upload rejected by Gateway: invalid content-length method=%s path=%s request_id=%s content_length=%s",
                request.method,
                request.url.path,
                request_id,
                content_length,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Content-Length header",
            )

        if request_size > settings.gateway_max_upload_request_size_bytes:
            gateway_logger.warning(
                "Upload rejected by Gateway: request too large method=%s path=%s request_id=%s request_size=%s max_size=%s",
                request.method,
                request.url.path,
                request_id,
                request_size,
                settings.gateway_max_upload_request_size_bytes,
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request body is too large",
            )

    headers = clean_request_headers(dict(request.headers))
    headers["X-Request-ID"] = request_id

    gateway_logger.info(
        "Forwarding request to Upload Service | method=%s target_url=%s request_id=%s",
        request.method,
        target_url,
        request_id,
    )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=dict(request.query_params),
                content=await request.body(),
            )

        gateway_logger.info(
            "Upload Service responded | method=%s target_url=%s status_code=%s request_id=%s",
            request.method,
            target_url,
            response.status_code,
            request_id,
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=clean_response_headers(dict(response.headers)),
            media_type=response.headers.get("content-type"),
        )

    except httpx.RequestError as error:
        gateway_logger.error(
            "Upload Service unavailable | method=%s target_url=%s error=%s request_id=%s",
            request.method,
            target_url,
            str(error),
            request_id,
        )

        raise HTTPException(
            status_code=503,
            detail="Upload Service is unavailable",
        )


@router.api_route(
    "/",
    methods=["GET", "POST"],
    summary="Forward upload root requests to Upload Service",
)
async def proxy_upload_root(request: Request):
    return await forward_upload_request(request)


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
    summary="Forward upload path requests to Upload Service",
)
async def proxy_upload_path(request: Request, path: str):
    return await forward_upload_request(request, path)
