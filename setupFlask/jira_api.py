from flask import Flask, request, jsonify
import requests
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# JIRA Configuration (Load from .env)
JIRA_URL = os.getenv("JIRA_URL")  # Example: https://yourcompany.atlassian.net
EMAIL = os.getenv("JIRA_EMAIL")  # Your Atlassian email
API_TOKEN = os.getenv("JIRA_API_TOKEN")  # Your JIRA API Token
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")  # JIRA Project Key

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Atlassian-Token": "no-check"  # Prevents XSRF errors
}

@app.route('/create_issue', methods=['POST'])
def create_issue():
    """Creates a JIRA issue from GPT request and logs request details for debugging"""

    # 🔹 Debugging: Print received headers & body
    print("\n🔹 Headers received:", request.headers)
    print("🔹 Data received:", request.json)

    # Extract data from request
    data = request.json
    summary = data.get("summary")
    description = data.get("description")
    issuetype = data.get("issuetype")  # Expecting either "Bug" or "Test"

    # Ensure required fields exist
    if not summary or not description or not issuetype:
        return jsonify({"error": "Missing required fields (summary, description, issuetype)"}), 400

    # Validate issuetype (must be either "Bug" or "Test")
    valid_issue_types = ["Bug", "Test"]
    if issuetype not in valid_issue_types:
        return jsonify({"error": "Invalid issue type. Use 'Bug' or 'Test'."}), 400

    # ✅ Debug log
    print(f"📝 Creating JIRA Issue - Type: {issuetype}")

    # Create JIRA Issue Payload
    issue_data = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issuetype},  # ✅ Dynamically setting issuetype
        }
    }

    # Send Request to JIRA
    try:
        response = requests.post(
            f"{JIRA_URL}/rest/api/2/issue",
            headers=HEADERS,
            auth=HTTPBasicAuth(EMAIL, API_TOKEN),
            json=issue_data
        )

        # Handle JIRA Response
        if response.status_code == 201:
            jira_response = response.json()
            print(f"✅ JIRA Issue Created: {jira_response['key']}")
            return jsonify({"message": "Issue Created", "key": jira_response["key"]}), 201
        else:
            print("❌ JIRA API Error:", response.text)
            return jsonify({"error": "Failed to create issue", "details": response.text}), response.status_code

    except requests.exceptions.RequestException as e:
        print("🚨 JIRA Connection Error:", str(e))
        return jsonify({"error": "JIRA connection failed", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)