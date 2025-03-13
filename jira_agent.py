import requests
import json
import sys

# Load Jira credentials from config file
with open("config.json", "r") as config_file:
    config = json.load(config_file)

JIRA_URL = f"{config['jira_url']}/rest/api/3/issue"
EMAIL = config["email"]
API_TOKEN = config["api_token"]
PROJECT_KEY = config["project_key"]

HEADERS = {"Content-Type": "application/json"}
AUTH = (EMAIL, API_TOKEN)

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
        print(f"✅ Bug Created: {summary}")
        print(f"🔗 JIRA Link: {response.json()['self']}")
    else:
        print(f"❌ Failed to create bug: {response.text}")

# Function to Create Multiple Bugs from a List
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