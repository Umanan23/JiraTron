import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# JIRA Configuration from .env
JIRA_URL = os.getenv("JIRA_URL") + "/rest/api/3/issue"
EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

HEADERS = {"Content-Type": "application/json"}
AUTH = (EMAIL, API_TOKEN)

# Function to create a test case in JIRA
def create_test_case(summary, preconditions, test_steps):
    issue_data = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    # Preconditions section
                    {"type": "paragraph", "content": [{"type": "text", "text": "📌 Preconditions:"}]},
                    {"type": "bulletList", "content": [
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": precondition}]}]}
                        for precondition in preconditions
                    ]},
                    # Test Steps Table
                    {"type": "paragraph", "content": [{"type": "text", "text": "📝 Test Steps Table:"}]},
                    {"type": "table", "attrs": {"isNumberColumnEnabled": False}, "content": [
                        {"type": "tableRow", "content": [
                            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Test Step"}]}]},
                            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Test Data"}]}]},
                            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Expected Result"}]}]}
                        ]}
                    ] + [
                        {"type": "tableRow", "content": [
                            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": step["step"]}]}]},
                            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": step["data"]}]}]},
                            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": step["expected"]}]}]}
                        ]}
                        for step in test_steps
                    ]}
                ]
            },
            "issuetype": {"name": "Test"}
        }
    }

    response = requests.post(JIRA_URL, headers=HEADERS, auth=AUTH, json=issue_data)

    if response.status_code == 201:
        print(f"✅ Test Case Created: {summary}")
        print(f"🔗 JIRA Link: {response.json()['self']}")
    else:
        print(f"❌ Failed to create test case: {response.text}")

# Example Test Case with Detailed Steps
test_case = {
    "summary": "Verify UI of Privacy & Security Page",
    "preconditions": [
        "User must be logged into Nucleus.",
        "User must navigate to Privacy & Security Page."
    ],
    "test_steps": [
        {"step": "Verify the page title and header text.", "data": "N/A", "expected": "The page title should be 'Privacy & Security' and the header should match it."},
        {"step": "Check if all sections are visible.", "data": "N/A", "expected": "All sections should be correctly displayed."},
        {"step": "Verify the availability of text fields, dropdowns, and buttons.", "data": "N/A", "expected": "Fields and buttons should be present."}
    ]
}

# Upload the test case to JIRA
create_test_case(test_case["summary"], test_case["preconditions"], test_case["test_steps"])