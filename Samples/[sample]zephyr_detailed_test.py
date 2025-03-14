import requests
import json
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# JIRA & Zephyr Squad API Credentials
JIRA_URL = os.getenv("JIRA_URL")
EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# Headers for API authentication
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def get_issue_types():
    """Check for Test-related issue types which would indicate Zephyr installation"""
    url = f"{JIRA_URL}/rest/api/2/issuetype"
    print(f"\nChecking issue types: {url}")
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN),
        headers=HEADERS
    )
    
    if response.status_code == 200:
        issue_types = response.json()
        test_related = [it for it in issue_types if 'test' in it.get('name', '').lower()]
        
        if test_related:
            print("✅ Found test-related issue types:")
            for it in test_related:
                print(f"- {it.get('name')}")
            return True
        else:
            print("❌ No test-related issue types found")
            return False
    else:
        print(f"❌ Failed to get issue types: {response.status_code}")
        return False

def check_more_zephyr_endpoints(project_id):
    """Try additional possible Zephyr endpoints"""
    additional_endpoints = [
        # Cloud-specific endpoints
        f"{JIRA_URL}/rest/atm/1.0/testcase",
        f"{JIRA_URL}/rest/tests/1.0/search",
        
        # Try some generic endpoints
        f"{JIRA_URL}/rest/zephyr-squad",
        f"{JIRA_URL}/rest/zephyr",
        
        # Try project-specific endpoints
        f"{JIRA_URL}/rest/api/2/project/{PROJECT_KEY}/issueTypes",
        
        # Try Zephyr Scale endpoints in case it's actually Scale
        f"{JIRA_URL}/rest/atm/1.0/testcase/search"
    ]
    
    print("\nTrying additional endpoints:")
    
    for endpoint in additional_endpoints:
        print(f"\nTrying endpoint: {endpoint}")
        try:
            response = requests.get(
                endpoint,
                auth=HTTPBasicAuth(EMAIL, API_TOKEN),
                headers=HEADERS
            )
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code != 404:
                print(f"✅ Endpoint potentially working: {endpoint}")
                print(f"Response sample: {str(response.text[:100])}...")
            else:
                print(f"❌ Endpoint not found: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def check_project_components():
    """Check if the project has any test management components"""
    url = f"{JIRA_URL}/rest/api/2/project/{PROJECT_KEY}/components"
    print(f"\nChecking project components: {url}")
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN),
        headers=HEADERS
    )
    
    if response.status_code == 200:
        components = response.json()
        test_related = [c for c in components if 'test' in c.get('name', '').lower() or 'zephyr' in c.get('name', '').lower()]
        
        if test_related:
            print("✅ Found test-related components:")
            for c in test_related:
                print(f"- {c.get('name')}")
            return True
        else:
            print("❌ No test-related components found")
            return False
    else:
        print(f"❌ Failed to get components: {response.status_code}")
        return False

def check_jira_version():
    """Check the Jira version which might affect Zephyr integration"""
    url = f"{JIRA_URL}/rest/api/2/serverInfo"
    print(f"\nChecking Jira server info: {url}")
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN),
        headers=HEADERS
    )
    
    if response.status_code == 200:
        info = response.json()
        print(f"✅ Jira version: {info.get('version')}")
        print(f"✅ Deployment type: {info.get('deploymentType', 'Unknown')}")
        return info
    else:
        print(f"❌ Failed to get server info: {response.status_code}")
        return None

def check_cloud_or_server():
    """Determine if this is Jira Cloud or Server/Data Center"""
    if "atlassian.net" in JIRA_URL:
        print("\n✅ This appears to be a Jira Cloud instance")
        return "Cloud"
    else:
        print("\n✅ This appears to be a Jira Server/Data Center instance")
        return "Server"

if __name__ == "__main__":
    print("=== Detailed Zephyr Squad Detection ===")
    print(f"Jira URL: {JIRA_URL}")
    print(f"Project Key: {PROJECT_KEY}")
    
    # Check if this is Cloud or Server
    deployment_type = check_cloud_or_server()
    
    # Check Jira version
    jira_info = check_jira_version()
    
    # Check for test-related issue types
    has_test_types = get_issue_types()
    
    # Check for test-related project components
    has_test_components = check_project_components()
    
    # Check more possible Zephyr endpoints
    check_more_zephyr_endpoints(PROJECT_KEY)
    
    print("\n=== Summary ===")
    print(f"Deployment Type: {deployment_type}")
    if jira_info:
        print(f"Jira Version: {jira_info.get('version')}")
    print(f"Test Issue Types Found: {'Yes' if has_test_types else 'No'}")
    print(f"Test Components Found: {'Yes' if has_test_components else 'No'}")
    
    if deployment_type == "Cloud":
        print("\n=== Recommendation for Jira Cloud ===")
        print("It appears you're using Jira Cloud. For Jira Cloud, you should:")
        print("1. Verify that Zephyr Squad is installed from the Atlassian Marketplace")
        print("2. For Jira Cloud, the correct API endpoints are likely:")
        print("   - For Zephyr Squad Cloud: /rest/zapi/latest/...")
        print("   - For Zephyr Scale Cloud: /rest/atm/1.0/...")
        print("3. Consider checking your API token permissions")
    else:
        print("\n=== Recommendation for Jira Server/Data Center ===")
        print("It appears you're using Jira Server/Data Center. You should:")
        print("1. Verify that Zephyr Squad is installed from the Atlassian Marketplace")
        print("2. For Jira Server, the correct API endpoints are likely:")
        print("   - For older versions: /rest/zapi/2.0/...")
        print("   - For newer versions: /rest/zephyr/1.0/...")
        print("3. Consider checking your API token permissions")