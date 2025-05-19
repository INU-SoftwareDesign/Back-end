import traceback
from django.utils.deprecation import MiddlewareMixin
from datetime import datetime
from utils.slack import send_error_slack

class SlackExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        start_time = getattr(request, "_start_time", datetime.now())
        request._start_time = start_time

        request.api_name = f"{request.method} {request.path}"

        send_error_slack(request, request.api_name, start_time)
        return None
    