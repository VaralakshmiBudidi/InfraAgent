from pydantic import BaseModel, HttpUrl, validator
from typing import Optional

class DeploymentRequest(BaseModel):
    prompt: str
    repo_url: Optional[HttpUrl] = None
    environment: Optional[str] = None

    @validator('environment')
    def validate_environment(cls, v):
        if v is not None:
            valid_envs = ['dev', 'qa', 'beta', 'prod']
            if v.lower() not in valid_envs:
                raise ValueError(f"Environment must be one of: {', '.join(valid_envs)}")
        return v.lower() if v else v

class RollbackRequest(BaseModel):
    deployment_id: str
