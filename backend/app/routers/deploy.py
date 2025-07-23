from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.deployment import DeploymentRequest, DeploymentResponse, DeploymentListResponse
from app.services.deploy_service import create_deployment
from app.services.deployment_storage import deployment_storage

router = APIRouter()

@router.post("/")
async def deploy(request: DeploymentRequest):
    """
    Create a deployment using AI to extract all necessary information from the user's prompt.
    The user only needs to provide a natural language description of what they want to deploy.
    """
    try:
        # Validate that prompt is provided
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(
                status_code=400, 
                detail="Please provide a description of what you want to deploy."
            )
        
        # Create deployment using AI extraction
        result = await create_deployment(request=request)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/status/{deployment_id}")
async def get_deployment_status(deployment_id: str):
    """Get the status of a specific deployment"""
    deployment = deployment_storage.get_deployment(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment

@router.get("/list")
async def list_deployments(
    limit: int = Query(50, ge=1, le=100, description="Number of deployments to return"),
    repo_url: Optional[str] = Query(None, description="Filter by repository URL"),
    environment: Optional[str] = Query(None, description="Filter by environment")
):
    """Get a list of all deployments with optional filtering"""
    if repo_url:
        deployments = deployment_storage.get_deployments_by_repo(repo_url)
    elif environment:
        deployments = deployment_storage.get_deployments_by_environment(environment)
    else:
        deployments = deployment_storage.get_all_deployments(limit)
    
    return DeploymentListResponse(
        deployments=deployments,
        total=len(deployments)
    )

@router.get("/recent")
async def get_recent_deployments(limit: int = Query(10, ge=1, le=50)):
    """Get recent deployments"""
    deployments = deployment_storage.get_all_deployments(limit)
    return DeploymentListResponse(
        deployments=deployments,
        total=len(deployments)
    )

