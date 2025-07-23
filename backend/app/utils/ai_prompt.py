import os
import json
from typing import Dict, Optional
from openai import OpenAI

def extract_deployment_info(prompt: str) -> Dict:
    """
    Use OpenAI to extract deployment information from natural language prompt.
    Returns a dictionary with repo_url, environment, and other deployment details.
    """
    try:
        # Initialize OpenAI client (v1.x syntax)
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY not found in environment variables")
        
        client = OpenAI(api_key=api_key)
        
        # Create a structured prompt for the AI
        system_prompt = """
        You are an AI assistant that extracts deployment information from user requests.
        Analyze the user's deployment request and extract the following information:
        
        1. GitHub repository URL (if mentioned or can be inferred)
        2. Target environment (dev, qa, beta, prod, staging)
        3. Deployment type/description
        4. Any specific requirements or configurations
        
        Return the information in JSON format with these fields:
        - repo_url: The GitHub repository URL (null if not found)
        - environment: Target environment (dev, qa, beta, prod, staging) or null if not specified
        - deployment_type: Type of deployment (web app, api, static site, etc.)
        - description: Detailed description of what to deploy
        - requirements: Any specific requirements mentioned
        - needs_repo_url: true if repository URL is missing and should be requested
        - needs_environment: true if environment is missing and should be requested
        
        If no repository is mentioned, set needs_repo_url to true.
        If no environment is mentioned, set needs_environment to true and environment to null.
        Do NOT default to 'dev' - only set environment if explicitly mentioned.
        """
        
        # Make the API call (v1.x syntax)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        # Parse the response
        ai_response = response.choices[0].message.content.strip()
        
        # Try to parse JSON from the response
        try:
            # Extract JSON from the response (in case there's extra text)
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = ai_response[json_start:json_end]
                result = json.loads(json_str)
            else:
                result = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback to regex parsing if JSON parsing fails
            result = fallback_parse(prompt)
        
        # Add missing fields if not present
        if 'needs_repo_url' not in result:
            result['needs_repo_url'] = result.get('repo_url') is None
        
        if 'needs_environment' not in result:
            result['needs_environment'] = result.get('environment') is None
        
        return result
        
    except Exception as e:
        print(f"Error in AI extraction: {str(e)}")
        # Fallback to regex parsing
        return fallback_parse(prompt)

def fallback_parse(prompt: str) -> Dict:
    """
    Fallback parsing using regex when AI fails.
    """
    import re
    
    # Extract GitHub URL
    github_match = re.search(r'https://github\.com/[^\s]+', prompt)
    repo_url = github_match.group(0) if github_match else None
    
    # Extract environment
    env_patterns = {
        'prod': r'\b(prod|production|live)\b',
        'beta': r'\b(beta|staging)\b', 
        'qa': r'\b(qa|test|testing)\b',
        'dev': r'\b(dev|development|local)\b'
    }
    
    environment = None  # Don't default to dev
    for env, pattern in env_patterns.items():
        if re.search(pattern, prompt, re.IGNORECASE):
            environment = env
            break
    
    return {
        'repo_url': repo_url,
        'environment': environment,
        'deployment_type': 'web application',
        'description': prompt,
        'requirements': None,
        'needs_repo_url': repo_url is None,
        'needs_environment': environment is None
    }

def parse_prompt(prompt: str) -> str:
    """
    Legacy function for backward compatibility.
    """
    result = extract_deployment_info(prompt)
    return result.get('repo_url', '')
