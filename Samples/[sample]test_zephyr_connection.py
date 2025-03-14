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

def test_jira_connection():
    """Test basic connection to Jira API"""
    url = f"{JIRA_URL}/rest/api/2/project/{PROJECT_KEY}"
    print(f"Testing connection to Jira API: {url}")
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN),
        headers=HEADERS
    )
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Connection to Jira API successful!")
        project_data = response.json()
        print(f"Project ID: {project_data.get('id')}")
        return True, project_data.get('id')
    else:
        print(f"❌ Connection failed: {response.text}")
        return False, None

def test_zephyr_endpoints(project_id):
    """Test various possible Zephyr Squad API endpoints"""
    
    # Different possible Zephyr endpoints to try
    possible_endpoints = [
        # Classic Zephyr Squad endpoints
        f"{JIRA_URL}/rest/zapi/2.0/cycle",
        f"{JIRA_URL}/rest/zapi/latest/cycle",
        
        # Cloud version endpoints
        f"{JIRA_URL}/rest/zephyr/1.0/cycle",
        
        # Other variations
        f"{JIRA_URL}/rest/zephyr-squad/1.0/cycle"
    ]
    
    print("\nTesting various Zephyr Squad endpoints:")
    
    for endpoint in possible_endpoints:
        print(f"\nTrying endpoint: {endpoint}")
        try:
            # Try to get cycles
            response = requests.get(
                endpoint,
                auth=HTTPBasicAuth(EMAIL, API_TOKEN),
                headers=HEADERS,
                params={"projectId": project_id}
            )
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Found working Zephyr endpoint: {endpoint}")
                print("Response sample: " + str(response.text[:100]) + "...")
                return True, endpoint
            else:
                print(f"❌ Endpoint not working: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing endpoint: {str(e)}")
    
    return False, None

def check_addon_versions():
    """Check installed add-ons to determine which Zephyr product is installed"""
    url = f"{JIRA_URL}/rest/plugins/1.0/"
    
    print("\nChecking installed add-ons:")
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(EMAIL, API_TOKEN),
            headers=HEADERS
        )
        
        if response.status_code == 200:
            plugins = response.json()
            zephyr_plugins = [p for p in plugins.get('plugins', []) 
                             if 'zephyr' in p.get('name', '').lower()]
            
            if zephyr_plugins:
                print("Found Zephyr plugins:")
                for plugin in zephyr_plugins:
                    print(f"- {plugin.get('name')} (v{plugin.get('version')})")
                return True, zephyr_plugins
            else:
                print("No Zephyr plugins found!")
                return False, []
        else:
            print(f"❌ Could not check add-ons: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Error checking add-ons: {str(e)}")
        return False, []

if __name__ == "__main__":
    print("=== Zephyr Squad Connection Test ===")
    print(f"Jira URL: {JIRA_URL}")
    print(f"Project Key: {PROJECT_KEY}\n")
    
    # Test Jira connection
    jira_connected, project_id = test_jira_connection()
    
    if jira_connected:
        # Check what Zephyr add-ons are installed
        addons_found, zephyr_plugins = check_addon_versions()
        
        # Test Zephyr endpoints
        if project_id:
            endpoint_found, working_endpoint = test_zephyr_endpoints(project_id)
            
            if endpoint_found:
                print("\n=== SUCCESS ===")
                print(f"Working Zephyr endpoint: {working_endpoint}")
                print("\nUpdate your code to use this endpoint!")
            else:
                print("\n=== FAILURE ===")
                print("Could not find a working Zephyr endpoint.")
                print("Please check if Zephyr Squad is properly installed and accessible.")
        else:
            print("Cannot test Zephyr endpoints without a project ID.")
    else:
        print("\n=== FAILURE ===")
        print("Could not connect to Jira API. Please check your credentials and URL.")