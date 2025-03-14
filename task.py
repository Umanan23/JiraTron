import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read Jira credentials from environment variables
JIRA_URL = f"{os.getenv('JIRA_URL')}/rest/api/3/issue"
EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

HEADERS = {"Content-Type": "application/json"}
AUTH = (EMAIL, API_TOKEN)

# Function to create a test case in JIRA
def create_test_case(summary, description):
    issue_data = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            },
            "issuetype": {"name": "Task"}
        }
    }

    response = requests.post(JIRA_URL, headers=HEADERS, auth=AUTH, json=issue_data)

    if response.status_code == 201:
        print(f"✅ Test Case Created: {summary}")
        print(f"🔗 JIRA Link: {response.json()['self']}")
    else:
        print(f"❌ Failed to create test case: {response.text}")

# Example Test Case Upload
create_test_case(
    "Verify UI Elements on Privacy & Security Page",
    "1. Verify page title.\n2. Check sections visibility.\n3. Validate fields and buttons.\n4. Ensure font/color consistency.\n5. Test responsiveness.\n6. Check error messages."
)