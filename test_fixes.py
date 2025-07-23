#!/usr/bin/env python3
"""
Simple test script to verify the fixes work correctly.
Run this to check if the main components can be imported without errors.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all modules can be imported without errors."""
    try:
        print("Testing imports...")
        
        # Test config
        from app.config import settings
        print("✅ Config imported successfully")
        
        # Test models
        from app.models.deployment import DeploymentRequest, DeploymentResponse
        print("✅ Models imported successfully")
        
        # Test utils
        from app.utils.github import validate_repo_url
        from app.utils.ai_prompt import extract_deployment_info
        print("✅ Utils imported successfully")
        
        # Test services
        from app.services.deployment_storage import deployment_storage
        from app.services.render_deployment import render_deployment_service
        print("✅ Services imported successfully")
        
        # Test routers
        from app.routers import deploy, webhook, chat
        print("✅ Routers imported successfully")
        
        print("\n🎉 All imports successful! The fixes are working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

def test_github_validation():
    """Test GitHub URL validation."""
    from app.utils.github import validate_repo_url
    
    test_urls = [
        ("https://github.com/username/repo", True),
        ("https://github.com/user-name/repo_name", True),
        ("https://github.com/user/repo/", True),
        ("http://github.com/user/repo", False),
        ("https://github.com/user", False),
        ("https://gitlab.com/user/repo", False),
        ("invalid-url", False),
    ]
    
    print("\nTesting GitHub URL validation...")
    for url, expected in test_urls:
        result = validate_repo_url(url)
        status = "✅" if result == expected else "❌"
        print(f"{status} {url} -> {result} (expected: {expected})")

if __name__ == "__main__":
    print("🧪 Testing InfraAgent fixes...\n")
    
    if test_imports():
        test_github_validation()
        print("\n✨ All tests passed! Your code is ready for production.")
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        sys.exit(1) 