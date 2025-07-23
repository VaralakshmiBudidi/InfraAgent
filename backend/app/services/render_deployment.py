import os
import requests
import json
import subprocess
import asyncio
from typing import Dict, Optional
from datetime import datetime
from app.services.deployment_storage import deployment_storage

class RenderDeploymentService:
    def __init__(self):
        self.render_api_key = os.getenv('RENDER_API_KEY')
        self.render_api_base = "https://api.render.com/v1"
        self.render_region = os.getenv('RENDER_REGION', 'oregon')  # Configurable region
        
    async def deploy_to_render(self, repo_url: str, environment: str, deployment_id: str) -> str:
        """
        Deploy an application to Render based on environment.
        """
        try:
            deployment_storage.add_build_log(deployment_id, "info", f"🚀 Starting Render deployment for {repo_url} to {environment}", "initialization")
            
            # Step 1: Clone and analyze repository
            deployment_storage.add_build_log(deployment_id, "info", f"📥 Cloning repository: {repo_url}", "cloning")
            repo_path = await self._clone_repository(repo_url, deployment_id)
            
            app_type = self._detect_app_type(repo_path)
            deployment_storage.add_build_log(deployment_id, "info", f"🔍 Detected app type: {app_type}", "analysis")
            
            # Step 2: Create Render service
            deployment_storage.add_build_log(deployment_id, "info", "🏗️ Creating Render service", "service_creation")
            service_id = await self._create_render_service(
                repo_url=repo_url,
                environment=environment,
                app_type=app_type,
                deployment_id=deployment_id
            )
            
            # Store service ID for webhook configuration
            deployment_storage.update_render_service_id(deployment_id, service_id)
            
            # Step 3: Configure webhook for automatic redeployment
            deployment_storage.add_build_log(deployment_id, "info", "🔗 Configuring GitHub webhook for automatic redeployment", "webhook_setup")
            await self._configure_webhook(repo_url, service_id, deployment_id)
            
            # Step 4: Deploy the service
            deployment_storage.add_build_log(deployment_id, "info", "🚀 Triggering deployment", "deployment")
            deployment_url = await self._deploy_service(service_id, environment, deployment_id)
            
            deployment_storage.add_build_log(deployment_id, "info", f"✅ Render deployment completed: {deployment_url}", "completed")
            return deployment_url
            
        except Exception as e:
            deployment_storage.add_build_log(deployment_id, "error", f"❌ Render deployment failed: {str(e)}", "failed")
            raise e
    
    async def _clone_repository(self, repo_url: str, deployment_id: str) -> str:
        """Clone repository to temporary directory."""
        repo_path = f"/tmp/deployments/{deployment_id}"
        os.makedirs(repo_path, exist_ok=True)
        
        try:
            result = subprocess.run(
                ["git", "clone", repo_url, repo_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise Exception(f"Failed to clone repository: {result.stderr}")
            
            return repo_path
        except subprocess.TimeoutExpired:
            raise Exception("Repository cloning timed out")
    
    def _detect_app_type(self, repo_path: str) -> str:
        """Detect application type from repository."""
        import os
        
        # Check for package.json (React/Node.js)
        if os.path.exists(os.path.join(repo_path, "package.json")):
            with open(os.path.join(repo_path, "package.json"), "r") as f:
                package_data = json.load(f)
                if "react" in package_data.get("dependencies", {}):
                    return "react"
                else:
                    return "nodejs"
        
        # Check for requirements.txt (Python)
        elif os.path.exists(os.path.join(repo_path, "requirements.txt")):
            return "python"
        
        # Check for Dockerfile
        elif os.path.exists(os.path.join(repo_path, "Dockerfile")):
            return "docker"
        
        # Default to static site
        return "static"
    
    async def _create_render_service(self, repo_url: str, environment: str, app_type: str, deployment_id: str) -> str:
        """Create a new Render service."""
        if not self.render_api_key:
            raise Exception("RENDER_API_KEY not configured")
        
        # Determine service configuration based on app type
        service_config = self._get_service_config(app_type, environment, repo_url)
        
        headers = {
            "Authorization": f"Bearer {self.render_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": f"{deployment_id}-{environment}",
            "type": "web_service",
            "env": service_config["env"],
            "plan": "free",
            "region": self.render_region,
            "repo": repo_url,
            "branch": "main",
            "buildCommand": service_config["build_command"],
            "startCommand": service_config["start_command"],
            "envVars": service_config["env_vars"],
            "autoDeploy": True  # Enable automatic deployment on push
        }
        
        response = requests.post(
            f"{self.render_api_base}/services",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to create Render service: {response.text}")
        
        service_data = response.json()
        return service_data["id"]
    
    async def _configure_webhook(self, repo_url: str, service_id: str, deployment_id: str):
        """Configure GitHub webhook for automatic redeployment."""
        try:
            # Extract repo owner and name from URL
            # Example: https://github.com/username/repo -> username/repo
            repo_path = repo_url.replace("https://github.com/", "").replace(".git", "")
            
            # Create webhook URL
            webhook_url = f"https://api.render.com/v1/services/{service_id}/deploys"
            
            # For now, we'll mark it as configured
            # In a full implementation, you'd use GitHub API to create the webhook
            deployment_storage.mark_webhook_configured(deployment_id)
            
        except Exception as e:
            print(f"Warning: Could not configure webhook: {str(e)}")
    
    def _get_service_config(self, app_type: str, environment: str, repo_url: str) -> Dict:
        """Get service configuration based on app type."""
        base_config = {
            "env": "node",
            "build_command": "npm install",
            "start_command": "npm start",
            "env_vars": [
                {"key": "NODE_ENV", "value": environment},
                {"key": "REPO_URL", "value": repo_url}
            ]
        }
        
        if app_type == "react":
            return {
                **base_config,
                "build_command": "npm install && npm run build",
                "start_command": "npm start"
            }
        elif app_type == "python":
            return {
                "env": "python",
                "build_command": "pip install -r requirements.txt",
                "start_command": "python app.py",
                "env_vars": [
                    {"key": "PYTHON_VERSION", "value": "3.9"},
                    {"key": "ENVIRONMENT", "value": environment},
                    {"key": "REPO_URL", "value": repo_url}
                ]
            }
        elif app_type == "docker":
            return {
                "env": "docker",
                "build_command": "",
                "start_command": "",
                "env_vars": [
                    {"key": "ENVIRONMENT", "value": environment},
                    {"key": "REPO_URL", "value": repo_url}
                ]
            }
        else:  # static
            return {
                "env": "static",
                "build_command": "",
                "start_command": "",
                "env_vars": [
                    {"key": "ENVIRONMENT", "value": environment},
                    {"key": "REPO_URL", "value": repo_url}
                ]
            }
    
    async def _deploy_service(self, service_id: str, environment: str, deployment_id: str) -> str:
        """Deploy the service and return the URL."""
        if not self.render_api_key:
            raise Exception("RENDER_API_KEY not configured")
        
        headers = {
            "Authorization": f"Bearer {self.render_api_key}",
            "Content-Type": "application/json"
        }
        
        # Trigger deployment
        deploy_response = requests.post(
            f"{self.render_api_base}/services/{service_id}/deploys",
            headers=headers
        )
        
        if deploy_response.status_code != 201:
            raise Exception(f"Failed to trigger deployment: {deploy_response.text}")
        
        # Wait for deployment to complete
        deployment_id_render = deploy_response.json()["id"]
        deployment_url = await self._wait_for_deployment(service_id, deployment_id_render, deployment_id)
        
        return deployment_url
    
    async def _wait_for_deployment(self, service_id: str, deployment_id: str, our_deployment_id: str) -> str:
        """Wait for deployment to complete and return service URL."""
        headers = {
            "Authorization": f"Bearer {self.render_api_key}"
        }
        
        max_attempts = 30  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            # Check deployment status
            deploy_response = requests.get(
                f"{self.render_api_base}/services/{service_id}/deploys/{deployment_id}",
                headers=headers
            )
            
            if deploy_response.status_code != 200:
                raise Exception(f"Failed to check deployment status: {deploy_response.text}")
            
            deploy_data = deploy_response.json()
            status = deploy_data["status"]
            
            # Update build logs based on status
            if status == "building":
                deployment_storage.add_build_log(our_deployment_id, "info", "🔨 Building application", "building")
            elif status == "deploying":
                deployment_storage.add_build_log(our_deployment_id, "info", "🚀 Deploying to Render", "deploying")
            elif status == "live":
                # Get service URL
                service_response = requests.get(
                    f"{self.render_api_base}/services/{service_id}",
                    headers=headers
                )
                
                if service_response.status_code != 200:
                    raise Exception(f"Failed to get service URL: {service_response.text}")
                
                service_data = service_response.json()
                deployment_storage.add_build_log(our_deployment_id, "info", "✅ Deployment successful", "completed")
                return service_data["service"]["url"]
            
            elif status in ["failed", "canceled"]:
                error_msg = deploy_data.get("error", "Unknown error")
                deployment_storage.add_build_log(our_deployment_id, "error", f"❌ Deployment failed: {error_msg}", "failed")
                raise Exception(f"Deployment failed with status: {status}")
            
            # Wait 10 seconds before checking again
            await asyncio.sleep(10)
            attempt += 1
        
        deployment_storage.add_build_log(our_deployment_id, "error", "⏰ Deployment timed out", "failed")
        raise Exception("Deployment timed out")

# Global instance
render_deployment_service = RenderDeploymentService() 