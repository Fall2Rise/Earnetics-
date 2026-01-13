import os
from typing import Optional
from fastapi import Request, Header, HTTPException

API_TOKEN = os.getenv('FALLAT_API_TOKEN')


def verify_token(token: str | None) -> bool:
    if API_TOKEN is None:
        return True
    return token == API_TOKEN


async def verify_request_token(
    request: Request,
    x_fallat_token: Optional[str] = Header(default=None, convert_underscores=False, alias="X-Fallat-Token"),
    x_api_token: Optional[str] = Header(default=None, convert_underscores=False, alias="X-Api-Token"),
) -> None:
    """FastAPI dependency to verify request token from headers."""
    # Allow localhost traffic without a token to keep the Command Center usable during setup
    client_host = request.client.host if request.client else None
    if client_host in ("127.0.0.1", "localhost", "::1"):
        return  # Always allow localhost for local development
    
    token = x_fallat_token or x_api_token
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid or missing API token")
