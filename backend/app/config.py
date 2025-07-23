import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # === GitHub Configuration ===
    github_token: Optional[str] = None
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "supersecret")  # Use env var with fallback

    # === Webhook Configuration ===
    webhook_url: str = "http://localhost:8000/webhook/github"

    # === Deployment Configuration ===
    deployment_dir: str = "/tmp/deployments"

    # === App Configuration ===
    environment: str = "development"
    debug: bool = True  # NOTE: Use 0/1 or true/false in .env

    class Config:
        env_file = ".env"  # Load from backend/.env automatically


# Create a global settings object to import throughout your app
settings = Settings()

