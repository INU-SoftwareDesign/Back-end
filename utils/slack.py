import requests
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(message):
    if not SLACK_WEBHOOK_URL:
        return

    payload = {
        "text": f":rotating_light: {message}"
    }

    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Slack alert failed: {e}")
