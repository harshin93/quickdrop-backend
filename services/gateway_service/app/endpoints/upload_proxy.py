import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from services.gateway_service.app.core.config import settings

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

    headers = clean_request_headers(dict(request.headers))

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=dict(request.query_params),
                content=await request.body(),
            )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=clean_response_headers(dict(response.headers)),
            media_type=response.headers.get("content-type"),
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Upload Service is unavailable",
        )


@router.api_route("/", methods=["GET", "POST"])
async def proxy_upload_root(request: Request):
    return await forward_upload_request(request)


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_upload_path(request: Request, path: str):
    return await forward_upload_request(request, path)
