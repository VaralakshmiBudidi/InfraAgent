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
    building = "building"
    deploying = "deploying"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"

class MessageType(str, Enum):
    user = "user"
    ai = "ai"

class ChatMessage(BaseModel):
    type: MessageType
    content: str
    timestamp: datetime = datetime.utcnow()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    needs_input: bool = False
    input_type: Optional[str] = None  # "repo_url", "environment", etc.
    suggestions: Optional[List[str]] = None

class DeploymentRequest(BaseModel):
    prompt: str  # Only require the user's natural language prompt

class DeploymentResponse(BaseModel):
    deployment_id: str
    status: str
    message: str
    extracted_info: dict  # AI-extracted information

class BuildLog(BaseModel):
    timestamp: datetime
    level: str  # "info", "warning", "error"
    message: str
    step: str  # "cloning", "building", "deploying"

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
    deployment_url: Optional[str] = None
    build_logs: List[BuildLog] = []
    render_service_id: Optional[str] = None
    webhook_configured: bool = False

class DeploymentListResponse(BaseModel):
    deployments: List[DeploymentRecord]
    total: int

class RollbackRequest(BaseModel):
    deployment_id: str
    reason: Optional[str] = None

class WebhookPayload(BaseModel):
    ref: str
    repository: dict
    commits: List[dict]
    head_commit: dict
