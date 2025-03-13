import requests
import json

# JIRA Configuration
JIRA_URL = "https://anaconda.atlassian.net/rest/api/3/issue"
EMAIL = "umanan@anaconda.com"
API_TOKEN = "your_api_token"
PROJECT_KEY = "HUB"

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

    headers = {"Content-Type": "application/json"}
    response = requests.post(JIRA_URL, headers=headers, auth=(EMAIL, API_TOKEN), data=json.dumps(issue_data))

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