import uuid
from app.utils.github import validate_repo_url, setup_webhook
from app.utils.ai_prompt import parse_prompt

async def create_deployment(request, environment=None, deployment_dir=None):
    # Step 1: Extract GitHub repo from prompt if not provided
    repo_url = request.repo_url or parse_prompt(request.prompt)

    if not repo_url or not validate_repo_url(repo_url):
        raise Exception("Invalid or missing GitHub repo URL.")

    # Step 2: Register webhook with GitHub for future deployments
    setup_webhook(repo_url)

    # Step 3: Use environment and deployment_dir as needed
    print(f"Deploying repo: {repo_url} | Environment: {environment} | Directory: {deployment_dir}")

    # Step 4: Perform initial deployment (simplified)
    deployment_id = str(uuid.uuid4())

    return {
        "message": "Deployment created successfully",
        "deployment_id": deployment_id,
        "repo_url": str(repo_url),  # Convert HttpUrl to string for JSON response
        "environment": environment,
        "deployment_dir": deployment_dir
    }
