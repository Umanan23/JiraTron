import requests
import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

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
                            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Test Result"}]}]}
                        ]}
                    ] + [
                        {"type": "tableRow", "content": [
                            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": step["step"]}]}]},
                            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": step["data"]}]}]},
                            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": step["Test Result"]}]}]}
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
        response_data = response.json()
        issue_key = response_data.get("key")  # Extract the actual Jira issue ID
        print(f"✅ Test Case Created: {summary}")
        print(f"🔗 JIRA Link: {JIRA_URL.replace('/rest/api/3/issue', '')}/browse/{issue_key}")  # Generate correct link
    else:
        print(f"❌ Failed to create test case: {response.text}")

# Function to load test cases from JSON file
def load_test_cases(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data["test_cases"]  # Ensure JSON has "test_cases" key
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return []

# Run the script
if __name__ == "__main__":
    test_cases_list = load_test_cases("test_cases.json")
    
    if test_cases_list:
        for test_case in test_cases_list:
            create_test_case(test_case["summary"], test_case["preconditions"], test_case["test_steps"])
    else:
        print("No test cases found in test_cases.json")