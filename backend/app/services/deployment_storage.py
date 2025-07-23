from typing import Dict, List, Optional
from datetime import datetime
import uuid
from app.models.deployment import DeploymentRecord, DeploymentStatus, BuildLog

class DeploymentStorage:
    def __init__(self):
        self.deployments: Dict[str, DeploymentRecord] = {}
    
    def create_deployment(self, repo_url: str, environment: str, prompt: str, deployment_dir: str = None) -> str:
        """Create a new deployment record"""
        deployment_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        deployment = DeploymentRecord(
            id=deployment_id,
            repo_url=repo_url,
            environment=environment,
            prompt=prompt,
            status=DeploymentStatus.pending,
            created_at=now,
            updated_at=now,
            deployment_dir=deployment_dir,
            build_logs=[]
        )
        
        self.deployments[deployment_id] = deployment
        return deployment_id
    
    def update_deployment_status(self, deployment_id: str, status: DeploymentStatus, error_message: str = None):
        """Update deployment status"""
        if deployment_id in self.deployments:
            deployment = self.deployments[deployment_id]
            deployment.status = status
            deployment.updated_at = datetime.utcnow()
            
            if status in [DeploymentStatus.completed, DeploymentStatus.failed, DeploymentStatus.cancelled]:
                deployment.completed_at = datetime.utcnow()
            
            if error_message:
                deployment.error_message = error_message
    
    def update_deployment_url(self, deployment_id: str, deployment_url: str):
        """Update deployment URL"""
        if deployment_id in self.deployments:
            deployment = self.deployments[deployment_id]
            deployment.deployment_url = deployment_url
            deployment.updated_at = datetime.utcnow()
    
    def add_build_log(self, deployment_id: str, level: str, message: str, step: str):
        """Add a build log entry"""
        if deployment_id in self.deployments:
            deployment = self.deployments[deployment_id]
            log_entry = BuildLog(
                timestamp=datetime.utcnow(),
                level=level,
                message=message,
                step=step
            )
            deployment.build_logs.append(log_entry)
            deployment.updated_at = datetime.utcnow()
    
    def update_render_service_id(self, deployment_id: str, service_id: str):
        """Update Render service ID"""
        if deployment_id in self.deployments:
            deployment = self.deployments[deployment_id]
            deployment.render_service_id = service_id
            deployment.updated_at = datetime.utcnow()
    
    def mark_webhook_configured(self, deployment_id: str):
        """Mark webhook as configured"""
        if deployment_id in self.deployments:
            deployment = self.deployments[deployment_id]
            deployment.webhook_configured = True
            deployment.updated_at = datetime.utcnow()
    
    def get_deployment(self, deployment_id: str) -> Optional[DeploymentRecord]:
        """Get a specific deployment by ID"""
        return self.deployments.get(deployment_id)
    
    def get_deployments_by_repo(self, repo_url: str) -> List[DeploymentRecord]:
        """Get all deployments for a specific repository"""
        return [d for d in self.deployments.values() if d.repo_url == repo_url]
    
    def get_latest_deployment_by_repo(self, repo_url: str) -> Optional[DeploymentRecord]:
        """Get the latest deployment for a specific repository"""
        deployments = self.get_deployments_by_repo(repo_url)
        if deployments:
            return max(deployments, key=lambda x: x.created_at)
        return None
    
    def get_all_deployments(self, limit: int = 50) -> List[DeploymentRecord]:
        """Get all deployments, sorted by creation date (newest first)"""
        deployments = list(self.deployments.values())
        deployments.sort(key=lambda x: x.created_at, reverse=True)
        return deployments[:limit]
    
    def get_deployments_by_environment(self, environment: str) -> List[DeploymentRecord]:
        """Get all deployments for a specific environment"""
        return [d for d in self.deployments.values() if d.environment == environment]

# Global instance
deployment_storage = DeploymentStorage() 