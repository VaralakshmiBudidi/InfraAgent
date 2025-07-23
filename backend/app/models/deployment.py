from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Environment(str, Enum):
    dev = "dev"
    qa = "qa"
    beta = "beta"
    prod = "prod"

class DeploymentStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"

class DeploymentRequest(BaseModel):
    prompt: str  # Only require the user's natural language prompt

class DeploymentResponse(BaseModel):
    deployment_id: str
    status: str
    message: str
    extracted_info: dict  # AI-extracted information

class DeploymentRecord(BaseModel):
    id: str
    repo_url: Optional[str] = None
    environment: str
    prompt: str
    deployment_type: Optional[str] = None
    requirements: Optional[str] = None
    status: DeploymentStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    deployment_dir: Optional[str] = None

class DeploymentListResponse(BaseModel):
    deployments: List[DeploymentRecord]
    total: int

class RollbackRequest(BaseModel):
    deployment_id: str
    reason: Optional[str] = None
