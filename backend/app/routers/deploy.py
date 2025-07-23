from fastapi import APIRouter, HTTPException
from app.models.deployment import DeploymentRequest
from app.services.deploy_service import create_deployment
from app.services.deployment_utils import get_deployment_preferences

router = APIRouter()

@router.post("/")
async def deploy(request: DeploymentRequest):
    try:
        # Validate required fields
        if not request.repo_url:
            raise HTTPException(
                status_code=400, 
                detail="GitHub repository URL is required. Please provide a valid repository URL."
            )
        
        # Extract environment from prompt or user input
        prefs = get_deployment_preferences(request.prompt, request.environment)
        
        # Now call create_deployment passing the request object
        result = await create_deployment(
            request=request,
            environment=prefs["environment"],
            deployment_dir=prefs["deployment_dir"]
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

