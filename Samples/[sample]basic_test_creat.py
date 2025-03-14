import requests
import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

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

def create_test_case(summary, preconditions, test_steps):
    """Creates a test case in Jira with the correct Jira issue key format"""
    url = f"{JIRA_URL}/rest/api/3/issue"
    
    # Get the correct issue type ID for "Test"
    issue_type_id = get_issue_type_id("Test")
    if not issue_type_id:
        issue_type_id = get_issue_type_id("QA Test")  # Try an alternative name
        
    if not issue_type_id:
        print("❌ Could not find a Test issue type ID")
        return None

    issue_data = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "📌 Preconditions:"}]},
                    {"type": "bulletList", "content": [
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": precondition}]}]}
                        for precondition in preconditions
                    ]},
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
            "issuetype": {"id": issue_type_id}  # Use the correct issue type ID
        }
    }

    response = requests.post(url, headers=HEADERS, auth=HTTPBasicAuth(EMAIL, API_TOKEN), json=issue_data)

    if response.status_code == 201:
        issue_key = response.json().get("key")  # Get the real Jira issue key
        print(f"✅ Test Case Created: {summary}")
        print(f"🔗 JIRA Link: {JIRA_URL}/browse/{issue_key}")  # Display proper Jira link
    else:
        print(f"❌ Failed to create test case: {response.status_code}")
        print(response.text)

def get_issue_type_id(issue_type_name):
    """Get the ID of an issue type by name"""
    url = f"{JIRA_URL}/rest/api/3/issuetype"
    
    response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(EMAIL, API_TOKEN))

    if response.status_code == 200:
        issue_types = response.json()
        for it in issue_types:
            if it.get('name') == issue_type_name:
                print(f"✅ Found issue type ID for '{issue_type_name}': {it.get('id')}")
                return it.get('id')

        print(f"❌ Issue type '{issue_type_name}' not found")
        return None
    else:
        print(f"❌ Failed to get issue types: {response.status_code}")
        return None

# Example Test Case
test_case = {
    "summary": "Verify UI of Privacy & Security Page",
    "preconditions": [
        "User must be logged into Nucleus.",
        "User must navigate to Privacy & Security Page."
    ],
    "test_steps": [
        {"step": "Verify the page title and header text.", "data": "N/A", "expected": "The page title should be 'Privacy & Security' and the header should match it."},
        {"step": "Check if all sections are visible.", "data": "N/A", "expected": "All sections should be correctly displayed."},
        {"step": "Verify the availability of text fields, dropdowns, and buttons.", "data": "N/A", "expected": "Fields and buttons should be present."},
        {"step": "Ensure all labels and text descriptions are readable.", "data": "N/A", "expected": "No missing, truncated, or misaligned text."},
        {"step": "Validate that icons (e.g., info/help icons) are correctly displayed.", "data": "N/A", "expected": "All icons should load properly and be aligned."},
        {"step": "Verify the color scheme and font consistency.", "data": "N/A", "expected": "The page should follow the standard UI theme."},
        {"step": "Check the presence and functionality of checkboxes and toggles.", "data": "N/A", "expected": "Checkboxes and toggles should be visible and interactable."},
        {"step": "Validate that the page is responsive across different screen sizes.", "data": "Open page on desktop & mobile", "expected": "The page layout should adjust correctly."},
        {"step": "Confirm that the footer and navigation bar are displayed properly.", "data": "N/A", "expected": "Navigation bar and footer should be present."},
        {"step": "Verify the error messages on invalid field input.", "data": "Enter invalid email/password", "expected": "Proper error messages should appear when incorrect data is entered."},
        {"step": "Check that links redirect correctly.", "data": "Click on any link", "expected": "Links should open the correct pages."},
        {"step": "Test the 'Save Settings' button.", "data": "Modify any setting and click Save", "expected": "Settings should be saved successfully."},
        {"step": "Ensure that the 'Reset Password' option works.", "data": "Click 'Reset Password'", "expected": "User should receive an email for password reset."},
        {"step": "Check if tooltips appear when hovering over help icons.", "data": "Hover over help icon", "expected": "Tooltips should display helpful text."},
        {"step": "Ensure session timeout works properly.", "data": "Leave page idle for 15 minutes", "expected": "User should be logged out after session expires."},
        {"step": "Check accessibility features.", "data": "Use a screen reader", "expected": "Screen reader should correctly read all page elements."}
    ]
}

# Upload the test case to JIRA
create_test_case(test_case["summary"], test_case["preconditions"], test_case["test_steps"])