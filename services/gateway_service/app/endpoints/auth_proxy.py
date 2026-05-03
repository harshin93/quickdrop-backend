from typing import Any

import httpx
from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import Response

from services.gateway_service.app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth Proxy"])


async def forward_request(request: Request, path: str):
    target_url = f"{settings.auth_service_url}/api/v1/auth/{path}"

    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        async with httpx.AsyncClient() as client:
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
            media_type=response.headers.get("content-type"),
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Auth Service is unavailable"
        )


@router.get("/{path:path}")
async def proxy_auth_get(request: Request, path: str):
    return await forward_request(request, path)


@router.post("/{path:path}")
async def proxy_auth_post(
    request: Request,
    path: str,
    body: Any = Body(default=None),
):
    return await forward_request(request, path)


@router.put("/{path:path}")
async def proxy_auth_put(
    request: Request,
    path: str,
    body: Any = Body(default=None),
):
    return await forward_request(request, path)


@router.delete("/{path:path}")
async def proxy_auth_delete(request: Request, path: str):
    return await forward_request(request, path)