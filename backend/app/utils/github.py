import requests
from app.config import settings

def validate_repo_url(url) -> bool:
    # Convert HttpUrl to string if needed
    url_str = str(url) if hasattr(url, '__str__') else url
    return url_str.startswith("https://github.com/")

def setup_webhook(repo_url):
    print(f"Setting up webhook for {repo_url}")
    
    # Skip webhook setup if GitHub token is not provided
    if not settings.github_token:
        print("⚠️ GitHub token not provided. Skipping webhook setup.")
        return
    
    # Convert HttpUrl to string if needed
    repo_url_str = str(repo_url) if hasattr(repo_url, '__str__') else repo_url
    
    # Extract owner and repo name from the URL
    try:
        parts = repo_url_str.rstrip("/").split("/")
        owner, repo = parts[-2], parts[-1]
    except IndexError:
        raise ValueError("Invalid GitHub repo URL.")

    api_url = f"https://api.github.com/repos/{owner}/{repo}/hooks"
    
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "name": "web",
        "active": True,
        "events": ["push"],
        "config": {
            "url": settings.webhook_url,
            "content_type": "json",
            "secret": settings.webhook_secret,
            "insecure_ssl": "0"
        }
    }

    try:
        response = requests.post(api_url, json=data, headers=headers)

        if response.status_code == 201:
            print("✅ Webhook successfully created.")
        elif response.status_code == 422 and "already exists" in response.text:
            print("ℹ️ Webhook already exists.")
        else:
            print(f"❌ Failed to create webhook: {response.status_code} | {response.text}")
            # Don't raise error, just log it
    except Exception as e:
        print(f"⚠️ Error setting up webhook: {str(e)}")
        # Don't raise error, just log it

