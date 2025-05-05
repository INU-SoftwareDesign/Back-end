import traceback
from django.utils.deprecation import MiddlewareMixin
from utils.slack import send_slack_alert

class SlackExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        message = f"[ERROR] {request.method} {request.path}\n{str(exception)}"
        tb = traceback.format_exc()

        send_slack_alert(f"{message}\n```\n{tb}\n```")
        return None
