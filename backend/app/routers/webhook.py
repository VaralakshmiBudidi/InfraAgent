import hmac
import hashlib
import json
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
    try:
        body = await request.body()

        if not verify_signature(body, x_hub_signature_256):
            raise HTTPException(status_code=403, detail="Invalid signature")

        payload = await request.json()
        
        # Validate payload structure
        if not payload or 'repository' not in payload:
            raise HTTPException(status_code=400, detail="Invalid webhook payload")
        
        repo_name = payload.get("repository", {}).get("full_name")
        if not repo_name:
            raise HTTPException(status_code=400, detail="Repository name not found in payload")

        print(f"✅ Webhook received from repo: {repo_name}")
        # TODO: Redeploy logic here
        return {"status": "ok", "repository": repo_name}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

