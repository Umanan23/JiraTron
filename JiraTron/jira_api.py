from flask import Flask, request, jsonify
import requests
import os
import re
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# JIRA Configuration (Load from .env)
JIRA_URL = os.getenv("JIRA_URL")           # e.g., you main jira url
EMAIL = os.getenv("JIRA_EMAIL")            # Your Atlassian email
API_TOKEN = os.getenv("JIRA_API_TOKEN")    # Your JIRA API Token
DEFAULT_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")  # Default Jira Project Key

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Atlassian-Token": "no-check"  # Prevents XSRF errors
}

# --- Formatting Functions

def format_bug_description(steps, actual, expected):
    """Formats bug details into a markdown description for Jira."""
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
    """
    Formats test case details into a Jira wiki-style table.
    Removes any leading numbering in the 'step' text.
    """
    description = f"*📝 Preconditions:*\n{preconditions}\n\n"
    # Wiki-style table header
    description += "|| Step || Test Data || Expected Result ||\n"
    for step in test_steps:
        raw_step = step.get("step", "")
        # Remove leading numbering (e.g., "1. " or "2) ")
        cleaned_step = re.sub(r'^\s*\d+[\.\)]?\s*', '', raw_step)
        test_data = step.get("test_data", "")
        expected = step.get("expected_result", "")
        description += f"| {cleaned_step} | {test_data} | {expected} |\n"
    return description

# --- Create Issue Endpoint

@app.route('/create_issue', methods=['POST'])
def create_issue():
    """
    Creates Jira issues from a GPT request.
    
    Supported issuetype values: Bug, Test, Task, Story, Epic.
    
    For Bugs and Tests:
      - If a non-empty description is provided, it is used.
      - Otherwise, detailed fields are used to build a description.
    
    **Multiple Test Cases Support:**
      - If the payload includes "issuetype": "Test" and a field "test_cases" (an array), 
        each element is processed as a separate test case.
    
    For Tasks, Stories, and Epics:
      - The description is set to an empty string.
    """
    data = request.json
    summary = data.get("summary")
    issuetype = data.get("issuetype")
    
    # Use the provided project key or default if omitted.
    project_key = data.get("project_key", DEFAULT_PROJECT_KEY)
    
    # Convert labels from comma-separated string to list if needed.
    labels_input = data.get("labels", [])
    if isinstance(labels_input, str):
        labels = [label.strip() for label in labels_input.split(",") if label.strip()]
    else:
        labels = labels_input

    # Validate required fields.
    if not summary or not issuetype:
        return jsonify({"error": "Missing required fields (summary, issuetype)"}), 400

    # Check if we need to process multiple test cases.
    if issuetype == "Test" and isinstance(data.get("test_cases"), list):
        results = []
        for tc in data["test_cases"]:
            # Each test case might have its own summary; if not, use the global summary.
            tc_summary = tc.get("summary", summary)
            tc_preconditions = tc.get("preconditions", "")
            tc_test_steps = tc.get("test_steps", [])
            # Build the description using our wiki-table formatter.
            description = format_test_case_description(tc_preconditions, tc_test_steps)
            issue_payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": tc_summary,
                    "description": description,
                    "issuetype": {"name": "Test"},  # Use the provided name "Test"
                    "labels": labels
                }
            }
            response = requests.post(
                f"{JIRA_URL}/rest/api/2/issue",
                headers=HEADERS,
                auth=HTTPBasicAuth(EMAIL, API_TOKEN),
                json=issue_payload
            )
            if response.status_code == 201:
                jira_response = response.json()
                results.append({"message": "Issue Created", "key": jira_response["key"]})
            else:
                results.append({"error": "Failed to create test case", "details": response.text})
        return jsonify(results), 201

    # Single issue processing (or non-Test issuetype)
    if issuetype in ["Bug", "Test"]:
        if data.get("description"):
            description = data.get("description")
        else:
            if not data.get("steps_to_reproduce") and not data.get("preconditions"):
                return jsonify({"error": "Missing required details for Bug/Test."}), 400
            if issuetype == "Bug":
                description = format_bug_description(
                    data.get("steps_to_reproduce", []),
                    data.get("actual_result", ""),
                    data.get("expected_result", "")
                )
            else:  # Test
                description = format_test_case_description(
                    data.get("preconditions", ""),
                    data.get("test_steps", [])
                )
    elif issuetype in ["Task", "Story", "Epic"]:
        description = ""
    else:
        return jsonify({"error": "Invalid issue type."}), 400

    issue_data = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
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

# --- Search Issues Endpoint

@app.route('/search_issues', methods=['GET'])
def search_issues():
    """
    Searches for Jira issues using a JQL query.
    Expects a query parameter 'jql'.
    """
    jql = request.args.get("jql")
    if not jql:
        return jsonify({"error": "Missing required query parameter: jql"}), 400

    search_url = f"{JIRA_URL}/rest/api/2/search"
    params = {"jql": jql}
    response = requests.get(
        search_url,
        headers=HEADERS,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN),
        params=params
    )

    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"error": "Failed to search issues", "details": response.text}), response.status_code

# --- Get Issue Details Endpoint

@app.route('/get_issue/<issue_key>', methods=['GET'])
def get_issue(issue_key):
    """
    Retrieves details for a specific Jira issue given its key or ID.
    """
    issue_url = f"{JIRA_URL}/rest/api/2/issue/{issue_key}"
    response = requests.get(issue_url, headers=HEADERS, auth=HTTPBasicAuth(EMAIL, API_TOKEN))
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"error": "Failed to retrieve issue", "details": response.text}), response.status_code

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)