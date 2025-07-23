import os
import subprocess
import asyncio
from app.models.deployment import DeploymentRequest, DeploymentResponse, DeploymentStatus
from app.utils.github import validate_repo_url, setup_webhook
from app.services.deployment_storage import deployment_storage
from app.utils.ai_prompt import extract_deployment_info

async def create_deployment(request: DeploymentRequest) -> DeploymentResponse:
    """
    Create a deployment using AI to extract all necessary information from the user's prompt.
    """
    try:
        # Step 1: Use AI to extract deployment information
        print(f"🤖 Analyzing deployment request: {request.prompt}")
        extracted_info = extract_deployment_info(request.prompt)
        
        repo_url = extracted_info.get('repo_url')
        environment = extracted_info.get('environment', 'dev')
        deployment_type = extracted_info.get('deployment_type', 'web application')
        requirements = extracted_info.get('requirements')
        
        print(f"📋 AI extracted info: {extracted_info}")
        
        # Step 2: Validate extracted information
        if not repo_url:
            raise ValueError("Could not identify a GitHub repository from your request. Please include a repository URL or mention the repository name.")
        
        if not validate_repo_url(repo_url):
            raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
        
        # Step 3: Create deployment record
        deployment_id = deployment_storage.create_deployment(
            repo_url=repo_url,
            environment=environment,
            prompt=request.prompt,
            deployment_dir=f"/tmp/deployments/{environment}"
        )
        
        # Update with AI-extracted details
        deployment = deployment_storage.get_deployment(deployment_id)
        if deployment:
            deployment.deployment_type = deployment_type
            deployment.requirements = requirements
        
        # Step 4: Update status to in_progress
        deployment_storage.update_deployment_status(deployment_id, DeploymentStatus.in_progress)
        
        # Step 5: Register webhook with GitHub for future deployments
        if repo_url:
            setup_webhook(repo_url)
        
        # Step 6: Simulate deployment process
        await simulate_deployment(deployment_id, repo_url, environment, deployment_type)
        
        return DeploymentResponse(
            deployment_id=deployment_id,
            status="success",
            message=f"Deployment initiated successfully for {repo_url} to {environment} environment",
            extracted_info=extracted_info
        )
        
    except Exception as e:
        # Update deployment status to failed if we have a deployment_id
        if 'deployment_id' in locals():
            deployment_storage.update_deployment_status(deployment_id, DeploymentStatus.failed, str(e))
        
        raise e

async def simulate_deployment(deployment_id: str, repo_url: str, environment: str, deployment_type: str):
    """
    Simulate the deployment process with status updates.
    """
    try:
        print(f"🚀 Deploying {deployment_type} from {repo_url} to {environment} environment")
        
        # Simulate deployment steps
        await asyncio.sleep(2)  # Simulate processing time
        
        # Update status to completed
        deployment_storage.update_deployment_status(deployment_id, DeploymentStatus.completed)
        
        print(f"✅ Deployment {deployment_id} completed successfully")
        
    except Exception as e:
        # Update status to failed
        deployment_storage.update_deployment_status(deployment_id, DeploymentStatus.failed, str(e))
        print(f"❌ Deployment {deployment_id} failed: {str(e)}")
        raise e
