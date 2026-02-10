
import hmac
import hashlib
from fastapi import Request, HTTPException, status
from src.config import Config

async def verify_signature(request: Request):
    """
    Verifies the GitHub webhook signature.
    """
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing signature")
    
    secret = Config.GITHUB_TOKEN # Ideally this should be a separate WEBHOOK_SECRET env var
    if not secret:
        # If no secret configured, we can't verify, so for safety we might fail or allow (dev mode)
        # Assuming production readiness, we should fail or warn.
        # For this implementation, let's assume WEBHOOK_SECRET is used or fallback to TOKEN.
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    payload_body = await request.body()
    expected_signature = "sha256=" + hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")
    
    return True
