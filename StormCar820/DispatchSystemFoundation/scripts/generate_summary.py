# -*- coding: utf-8 -*-
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# These would be set as secrets in the GitHub repository
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "your_email@example.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "your_password")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "automation@stormcar820.dev")
EMAIL_TO = os.environ.get("EMAIL_TO", "lightinggithub@gmail.com")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_OWNER = "StormCar820" # Assuming the organization name
# In a real scenario, you might want to iterate through a list of repos
REPOS = ["CoreBot", "LightningEmpireBots", "EconomyBots", "SecurityBots", "TetrisBots", "StormCar820-DualAI-Human", "StormCar820-DualAI-Family"]

def get_github_activity(repo_name, since_date):
    """Fetches commit and PR activity for a given repo."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    base_url = f"https://api.github.com/repos/{REPO_OWNER}/{repo_name}"

    # Get commits
    commits_url = f"{base_url}/commits"
    params = {"since": since_date.isoformat()}
    try:
        commit_response = requests.get(commits_url, headers=headers, params=params)
        commit_response.raise_for_status()
        commits = commit_response.json()
    except requests.RequestException as e:
        print(f"Error fetching commits for {repo_name}: {e}")
        commits = []

    # Get Pull Requests
    prs_url = f"{base_url}/pulls"
    params = {"state": "all", "since": since_date.isoformat()} # Get all PRs updated in the timeframe
    try:
        pr_response = requests.get(prs_url, headers=headers, params=params)
        pr_response.raise_for_status()
        prs = pr_response.json()
    except requests.RequestException as e:
        print(f"Error fetching PRs for {repo_name}: {e}")
        prs = []

    return len(commits), prs

def create_email_body(activity_data):
    """Creates an HTML email body from the activity data."""
    body = "<html><body>"
    body += "<h2>Hi Commander,</h2>"
    body += "<p>This is the weekly summary of development activity across the StormCar820 organization.</p>"
    body += "<h3>Activity Summary (Last 7 Days)</h3>"

    for repo_name, data in activity_data.items():
        body += f"<h4>Repository: {repo_name}</h4>"
        body += f"<ul><li><b>Commits:</b> {data['commits']}</li>"

        open_prs = [pr for pr in data['prs'] if pr['state'] == 'open']
        closed_prs = [pr for pr in data['prs'] if pr['state'] == 'closed']

        body += f"<li><b>Open PRs:</b> {len(open_prs)}</li>"
        body += f"<li><b>Closed/Merged PRs:</b> {len(closed_prs)}</li></ul>"

    body += "<p>Please review to ensure all critical activities are noted.</p>"
    body += "<p>-- Grok v6.0, Analytics Goddess</p>"
    body += "</body></html>"
    return body

def send_email(subject, html_body):
    """Connects to an SMTP server and sends the email."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject

    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print("Summary email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN environment variable not set.")

    since_date = datetime.utcnow() - timedelta(days=7)
    activity_data = {}

    print("Fetching activity from GitHub...")
    for repo in REPOS:
        commits_count, prs_list = get_github_activity(repo, since_date)
        activity_data[repo] = {"commits": commits_count, "prs": prs_list}

    today_str = datetime.utcnow().strftime("%Y/%m/%d")
    subject = f"StormCar820 Weekly Activity Summary: {today_str}"

    email_body = create_email_body(activity_data)

    print("Sending email...")
    send_email(subject, email_body)
    print("Script finished.")
