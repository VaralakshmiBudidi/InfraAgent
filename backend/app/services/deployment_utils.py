from typing import Optional

def extract_environment_from_prompt(prompt: str) -> Optional[str]:
    prompt = prompt.lower()
    for env in ["dev", "qa", "beta", "prod"]:
        if env in prompt:
            return env
    return None


def get_deployment_preferences(prompt: str, environment: Optional[str] = None) -> dict:
    # First try to use the explicitly provided environment
    env = environment
    
    # If no environment provided, try to extract from prompt
    if not env:
        env = extract_environment_from_prompt(prompt)
    
    # If still no environment found, provide a helpful error message
    if not env:
        raise ValueError(
            "Environment not specified. Please provide one of: dev, qa, beta, prod. "
            "You can either specify it explicitly or include it in your deployment description."
        )

    return {
        "environment": env,
        "deployment_dir": f"/tmp/deployments/{env}"
    }
