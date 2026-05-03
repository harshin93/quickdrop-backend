from typing import Any

import httpx
from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import Response

from services.gateway_service.app.core.config import settings
from services.gateway_service.app.core.logging import gateway_logger

router = APIRouter(prefix="/auth", tags=["Auth Proxy"])


async def forward_request(request: Request, path: str):
    target_url = f"{settings.auth_service_url}/api/v1/auth/{path}"

    request_id = getattr(
        request.state,
        "request_id",
        request.headers.get("X-Request-ID", "unknown"),
    )

    headers = dict(request.headers)
    headers.pop("host", None)
    headers["X-Request-ID"] = request_id

    gateway_logger.info(
        "Forwarding request to Auth Service | method=%s target_url=%s request_id=%s",
        request.method,
        target_url,
        request_id,
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=dict(request.query_params),
                content=await request.body(),
            )

        gateway_logger.info(
            "Auth Service responded | method=%s target_url=%s status_code=%s request_id=%s",
            request.method,
            target_url,
            response.status_code,
            request_id,
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.headers.get("content-type"),
        )

    except httpx.RequestError as error:
        gateway_logger.error(
            "Auth Service unavailable | method=%s target_url=%s error=%s request_id=%s",
            request.method,
            target_url,
            str(error),
            request_id,
        )

        raise HTTPException(
            status_code=503,
            detail="Auth Service is unavailable"
        )


@router.get("/{path:path}", summary="Forward GET requests to Auth Service")
async def proxy_auth_get(request: Request, path: str):
    return await forward_request(request, path)


@router.post("/{path:path}", summary="Forward POST requests to Auth Service")
async def proxy_auth_post(
    request: Request,
    path: str,
    body: Any = Body(default=None),
):
    return await forward_request(request, path)


@router.put("/{path:path}", summary="Forward PUT requests to Auth Service")
async def proxy_auth_put(
    request: Request,
    path: str,
    body: Any = Body(default=None),
):
    return await forward_request(request, path)


@router.delete("/{path:path}", summary="Forward DELETE requests to Auth Service")
async def proxy_auth_delete(request: Request, path: str):
    return await forward_request(request, path)