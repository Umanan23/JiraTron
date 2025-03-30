from flask import Flask, request, jsonify
import requests
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# JIRA Configuration (Load from .env)
JIRA_URL = os.getenv("JIRA_URL")  # e.g., https://usamamanan.atlassian.net
EMAIL = os.getenv("JIRA_EMAIL")   # Your Atlassian email
API_TOKEN = os.getenv("JIRA_API_TOKEN")  # Your JIRA API Token
DEFAULT_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")  # Default JIRA Project Key

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Atlassian-Token": "no-check"  # Prevents XSRF errors
}

def format_bug_description(steps, actual, expected):
    """Formats the bug details (excluding summary) into a markdown description for JIRA."""
    steps_formatted = "\n".join([f"- {step}" for step in steps])
    return f"""
*🛠 Steps to Reproduce:*  
{steps_formatted}

*❌ Actual Result:*  
{actual}

*✅ Expected Result:*  
{expected}

*🌍 Environment:*  
- **OS:** Windows 11 x64  
- **Browsers:** Chrome, Firefox, Edge
"""

def format_test_case_description(preconditions, test_steps):
    """Formats the test case details (excluding summary) into a markdown description for JIRA."""
    test_case_desc = f"*📝 Preconditions:*\n{preconditions}\n\n*🛠 Test Steps:*\n"
    for step in test_steps:
        test_case_desc += (
            f"- **Step:** {step['step']}\n"
            f"  **Test Data:** {step['test_data']}\n"
            f"  **Expected Result:** {step['expected_result']}\n\n"
        )
    return test_case_desc

@app.route('/create_issue', methods=['POST'])
def create_issue():
    """Creates a JIRA issue from GPT request, using a dynamic project key and dynamic labels if provided."""
    
    data = request.json
    summary = data.get("summary")
    issuetype = data.get("issuetype")
    
    # Use project_key from the request if available; otherwise, use the default.
    project_key = data.get("project_key", DEFAULT_PROJECT_KEY)
    
    # Convert labels from a comma-separated string to a list, if necessary.
    labels_input = data.get("labels", [])
    if isinstance(labels_input, str):
        labels = [label.strip() for label in labels_input.split(",") if label.strip()]
    else:
        labels = labels_input

    # Check for required fields.
    if not summary or not issuetype or not data.get("description"):
        return jsonify({"error": "Missing required fields (summary, description, issuetype)"}), 400

    # Build description based on issue type.
    if issuetype == "Bug":
        description = format_bug_description(
            data.get("steps_to_reproduce", []),
            data.get("actual_result", ""),
            data.get("expected_result", "")
        )
    else:  # For Test Cases
        description = format_test_case_description(
            data.get("preconditions", ""),
            data.get("test_steps", [])
        )

    # Construct the payload, including dynamic project key and labels.
    issue_data = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,  # Used exclusively for the title.
            "description": description,
            "issuetype": {"name": issuetype},
            "labels": labels
        }
    }

    response = requests.post(
        f"{JIRA_URL}/rest/api/2/issue",
        headers=HEADERS,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN),
        json=issue_data
    )

    if response.status_code == 201:
        jira_response = response.json()
        return jsonify({"message": "Issue Created", "key": jira_response["key"]}), 201
    else:
        return jsonify({"error": "Failed to create issue", "details": response.text}), response.status_code

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)