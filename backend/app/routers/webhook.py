import hmac
import hashlib
from fastapi import APIRouter, Request, Header, HTTPException
from app.config import settings

router = APIRouter()

def verify_signature(payload: bytes, signature: str) -> bool:
    """
    Verifies the GitHub webhook signature.
    """
    if not signature:
        return False

    secret = settings.webhook_secret.encode()
    computed_signature = hmac.new(secret, msg=payload, digestmod=hashlib.sha256).hexdigest()
    expected = f"sha256={computed_signature}"

    return hmac.compare_digest(expected, signature)


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None)
):
    body = await request.body()

    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()
    repo_name = payload.get("repository", {}).get("full_name")

    print(f"✅ Webhook received from repo: {repo_name}")
    # TODO: Redeploy logic here
    return {"status": "ok"}

