import requests
import json
import os
import re
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load environment variables from .env
load_dotenv()

# JIRA Configuration
JIRA_URL = os.getenv("JIRA_URL")
EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Function to parse bug details from pasted text
def parse_bug_details(pasted_text):
    """Extracts bug details from a single pasted input"""

    title_match = re.search(r"Title:\s*(.+)", pasted_text)
    environment_match = re.search(r"Environment:\s*(.+?)(?=\n\n|\Z)", pasted_text, re.DOTALL)
    description_match = re.search(r"Description:\s*(.+?)(?=\n\n|\Z)", pasted_text, re.DOTALL)
    steps_match = re.search(r"Steps to Reproduce:\s*(.+?)(?=\n\n|\Z)", pasted_text, re.DOTALL)
    expected_match = re.search(r"Expected Behavior:\s*(.+?)(?=\n\n|\Z)", pasted_text, re.DOTALL)
    actual_match = re.search(r"Actual Behavior:\s*(.+?)(?=\n\n|\Z)", pasted_text, re.DOTALL)

    title = title_match.group(1).strip() if title_match else "Untitled Bug"
    environment = environment_match.group(1).strip() if environment_match else "Not specified"
    description = description_match.group(1).strip() if description_match else "No description provided"

    steps = []
    if steps_match:
        steps_raw = steps_match.group(1).strip().split("\n")
        for step in steps_raw:
            step = step.strip()
            if step:
                steps.append(re.sub(r"^\d+\.\s*", "", step))

    expected = expected_match.group(1).strip() if expected_match else "Not specified"
    actual = actual_match.group(1).strip() if actual_match else "Not specified"

    return title, environment, description, steps, expected, actual

# ✅ Function to format bug description as a plain string (instead of ADF)
def format_bug_description(title, environment, description, steps, expected, actual):
    """Formats bug details as a plain string for Jira API"""

    bug_description = f"""
    *Title:* {title}

    *🌍 Environment:*
    {environment}

    *📌 Description:*
    {description}

    *🛠 Steps to Reproduce:*
    """
    
    for index, step in enumerate(steps, 1):
        bug_description += f"{index}. {step}\n"

    bug_description += f"""
    
    *✅ Expected Behavior:*
    {expected}

    *❌ Actual Behavior:*
    {actual}
    """

    return bug_description.strip()

# Function to create a bug in Jira
def create_bug():
    """Creates a Bug in Jira with formatted description"""

    print("\n📢 Paste the full bug details and press Enter (Type 'done' on a new line to finish):")
    pasted_text = ""
    while True:
        line = input()
        if line.strip().lower() == "done":
            break
        pasted_text += line + "\n"

    title, environment, description, steps, expected, actual = parse_bug_details(pasted_text)

    issue_data = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": title,
            "description": format_bug_description(title, environment, description, steps, expected, actual),
            "issuetype": {"name": "Bug"},
            "priority": {"name": "High"},
            "labels": ["Bug", "Automation"]
        }
    }

    send_jira_request(issue_data, title, "Bug")


# ✅ Function to format test case as a plain string (instead of ADF)
def format_test_case_description(preconditions, test_steps):
    """Formats test case details as a plain string"""

    test_case_description = "*📌 Preconditions:*\n"
    for condition in preconditions:
        test_case_description += f"- {condition.strip()}\n"

    test_case_description += "\n*📝 Test Steps:*\n"
    for step in test_steps:
        test_case_description += f"- *Step:* {step['step']}\n  *Test Data:* {step['data']}\n  *Expected Result:* {step['expected']}\n\n"

    return test_case_description.strip()

# Function to create a test case in Jira
def create_test_case():
    """Creates a Test Case in Jira with formatted test steps"""

    print("\n📢 Enter Test Case Title:")
    title = input().strip()

    print("\n📌 Enter Precondition(s) (Separate with ';' for multiple preconditions):")
    preconditions = input().strip().split(";")

    print("\n📝 Enter Test Steps (Format: Step | Test Data | Expected Result, one per line, type 'done' when finished):")
    test_steps = []
    while True:
        step = input().strip()
        if step.lower() == "done":
            break
        parts = step.split("|")
        if len(parts) == 3:
            test_steps.append({"step": parts[0].strip(), "data": parts[1].strip(), "expected": parts[2].strip()})
        else:
            print("⚠️ Invalid format. Please enter in format: Step | Test Data | Expected Result")

    issue_data = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": title,
            "description": format_test_case_description(preconditions, test_steps),
            "issuetype": {"name": "Test"}
        }
    }

    send_jira_request(issue_data, title, "Test Case")


# Function to send a request to Jira
def send_jira_request(issue_data, title, issue_type):
    """Sends a request to Jira to create an issue"""
    response = requests.post(
        f"{JIRA_URL}/rest/api/2/issue",
        headers=HEADERS,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN),
        data=json.dumps(issue_data)
    )

    if response.status_code == 201:
        jira_response = response.json()
        jira_key = jira_response["key"]
        jira_url = f"{JIRA_URL}/browse/{jira_key}"
        print(f"✅ {issue_type} '{title}' created successfully in Jira: {jira_url}")
    else:
        print(f"❌ Failed to create {issue_type} '{title}' in Jira. Status Code: {response.status_code}")
        print(f"Response: {response.text}")

# Main function to choose between creating a bug or a test case
def main():
    while True:
        print("\n===== 🛠 JIRA Automation Tool 🛠 =====")
        print("1. Create Bug")
        print("2. Create Test Case")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1/2/3): ").strip()

        if choice == "1":
            create_bug()
        elif choice == "2":
            create_test_case()
        elif choice == "3":
            print("Exiting... 🚀")
            break
        else:
            print("❌ Invalid choice! Please enter 1, 2, or 3.")

# Run the script
if __name__ == "__main__":
    main()