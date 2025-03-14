import requests
import json
import sys
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load environment variables from .env file
load_dotenv()

# Read credentials from environment variables
JIRA_URL = f"{os.getenv('JIRA_URL')}/rest/api/3/issue"
EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
AUTH = HTTPBasicAuth(EMAIL, API_TOKEN)

# Function to Create a Bug in Jira
def create_bug(summary, steps, actual_result, expected_result, environment):
    issue_data = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": f"Steps to Reproduce:\n{steps}"}]},
                    {"type": "paragraph", "content": [{"type": "text", "text": f"Actual Result:\n{actual_result}"}]},
                    {"type": "paragraph", "content": [{"type": "text", "text": f"Expected Result:\n{expected_result}"}]},
                    {"type": "paragraph", "content": [{"type": "text", "text": f"Environment:\n{environment}"}]},
                ]
            },
            "issuetype": {"name": "Bug"}
        }
    }

    response = requests.post(JIRA_URL, headers=HEADERS, auth=AUTH, json=issue_data)

    if response.status_code == 201:
        response_data = response.json()
        issue_key = response_data.get("key", "UNKNOWN")  # Get the actual Jira issue key
        print(f"✅ Bug Created: {summary}")
        print(f"🔗 JIRA Link: https://anaconda.atlassian.net/browse/{issue_key}")
    else:
        print(f"❌ Failed to create bug: {response.status_code}")
        print(response.text)

# Function to Create Multiple Bugs from a JSON File
def create_multiple_bugs(bugs_list):
    for bug in bugs_list:
        create_bug(
            summary=bug["summary"],
            steps=bug["steps"],
            actual_result=bug["actual_result"],
            expected_result=bug["expected_result"],
            environment=bug["environment"]
        )

# Function to Load Bugs from a JSON File
def load_bugs_from_json(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data["bugs"]  # Ensure JSON has a "bugs" key
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        sys.exit(1)

# Run the script
if __name__ == "__main__":
    bugs_list = load_bugs_from_json("bugs.json")
    create_multiple_bugs(bugs_list)