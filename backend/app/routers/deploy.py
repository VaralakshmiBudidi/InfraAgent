from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional
from app.models.deployment import DeploymentRequest, DeploymentResponse, DeploymentListResponse, WebhookPayload
from app.services.deploy_service import create_deployment
from app.services.deployment_storage import deployment_storage
from app.services.render_deployment import render_deployment_service
import requests

router = APIRouter()

@router.post("/")
async def deploy(request: DeploymentRequest):
    """
    Create a deployment using AI to extract all necessary information from the user's prompt.
    The user only needs to provide a natural language description of what they want to deploy.
    """
    try:
        print(f"🚀 Deployment request received: {request.prompt}")
        
        # Validate that prompt is provided
        if not request.prompt or not request.prompt.strip():
            print("❌ Empty prompt received")
            raise HTTPException(
                status_code=400, 
                detail="Please provide a description of what you want to deploy."
            )
        
        # Create deployment using AI extraction
        print("🤖 Starting AI extraction...")
        result = await create_deployment(request=request)
        print(f"✅ Deployment result: {result}")
        return result
        
    except ValueError as e:
        print(f"❌ ValueError in deployment: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Exception in deployment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/status/{deployment_id}")
async def get_deployment_status(deployment_id: str):
    """Get the status of a specific deployment"""
    deployment = deployment_storage.get_deployment(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment

@router.get("/logs/{deployment_id}")
async def get_deployment_logs(deployment_id: str):
    """Get build logs for a specific deployment"""
    deployment = deployment_storage.get_deployment(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return {
        "deployment_id": deployment_id,
        "status": deployment.status,
        "build_logs": deployment.build_logs,
        "total_logs": len(deployment.build_logs)
    }

@router.post("/webhook/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook for automatic redeployment"""
    try:
        # Get the webhook payload
        payload = await request.json()
        
        # Extract repository information
        repo_url = f"https://github.com/{payload['repository']['full_name']}"
        commit_message = payload['head_commit']['message']
        commit_id = payload['head_commit']['id']
        
        print(f"🔔 GitHub webhook received for {repo_url}")
        print(f"📝 Commit: {commit_message} ({commit_id})")
        
        # Find the latest deployment for this repository
        latest_deployment = deployment_storage.get_latest_deployment_by_repo(repo_url)
        
        if not latest_deployment:
            print(f"❌ No deployment found for repository: {repo_url}")
            return {"message": "No deployment found for repository"}
        
        if not latest_deployment.render_service_id:
            print(f"❌ No Render service ID found for deployment: {latest_deployment.id}")
            return {"message": "No Render service ID found"}
        
        # Trigger redeployment
        print(f"🔄 Triggering redeployment for {latest_deployment.id}")
        
        # Add webhook log
        deployment_storage.add_build_log(
            latest_deployment.id,
            "info",
            f"🔄 Automatic redeployment triggered by commit: {commit_message}",
            "webhook"
        )
        
        # Trigger new deployment on Render
        headers = {
            "Authorization": f"Bearer {render_deployment_service.render_api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{render_deployment_service.render_api_base}/services/{latest_deployment.render_service_id}/deploys",
            headers=headers
        )
        
        if response.status_code == 201:
            deployment_storage.add_build_log(
                latest_deployment.id,
                "info",
                "✅ Redeployment triggered successfully",
                "webhook"
            )
            return {"message": "Redeployment triggered successfully"}
        else:
            deployment_storage.add_build_log(
                latest_deployment.id,
                "error",
                f"❌ Failed to trigger redeployment: {response.text}",
                "webhook"
            )
            return {"message": "Failed to trigger redeployment"}
            
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return {"message": "Error processing webhook"}

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

