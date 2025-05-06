import requests
import os
from datetime import datetime

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def _send_slack(message: str, emoji: str):
    if not SLACK_WEBHOOK_URL:
        return
    try:
        requests.post(SLACK_WEBHOOK_URL, json={"text": f"{emoji} {message}"})
    except Exception as e:
        print(f"Slack alert failed: {e}")

def send_success_slack(request, api_name: str, start_time: datetime):
    duration = (datetime.now() - start_time).total_seconds()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = (
        f"{request.user.name} ({request.user.username})"
        if request.user.is_authenticated else "비로그인 사용자"
    )
    message = (
        f"[API 처리 성공]\n"
        f"- API: {api_name}\n"
        f"- 사용자: {user}\n"
        f"- 발생 시각: {now}\n"
        f"- 처리시간: {duration:.2f}초\n"
        f"- 요청 URL: {request.get_full_path()}"
    )
    _send_slack(message, ":white_check_mark:")

def send_error_slack(request, api_name: str, start_time: datetime):
    duration = (datetime.now() - start_time).total_seconds()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = (
        f"{request.user.name} ({request.user.username})"
        if request.user.is_authenticated else "비로그인 사용자"
    )
    message = (
        f"[API 처리 오류]\n"
        f"- API: {api_name}\n"
        f"- 사용자: {user}\n"
        f"- 발생 시각: {now}\n"
        f"- 처리시간: {duration:.2f}초\n"
        f"- 요청 URL: {request.get_full_path()}"
    )
    _send_slack(message, ":rotating_light:")
